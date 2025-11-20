from datetime  import datetime,timezone,timedelta
from math import radians,sin,cos,asin,sqrt
from random import uniform,seed,choice,choices,randint,sample,random
from faker import Faker
import uuid
import argparse
import json
import logging
import redis
import signal
import threading

LOG = logging.getLogger("simulator")
faker = Faker()

def gen_iso():
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

def dis_calc_in_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * asin(sqrt(a))

def noise_to_dist_adder(lat, lon, km_radius=10):
    delta_deg = km_radius / 111.0
    return lat + uniform(-delta_deg, delta_deg), lon +uniform(-delta_deg, delta_deg)


class Userprofile:
    def __init__(self,n_user = 200,cities = None,set_seed = None):
        self.users ={}
        self.n = n_user
        self.cities = cities or[
                            ("Delhi", 28.6100, 77.2300),
                            ("Mumbai", 19.0761, 72.8775),
                            ("Kolkāta", 22.5675, 88.3700),
                            ("Bangalore", 12.9789, 77.5917),
                            ("Chennai", 13.0825, 80.2750),
                            ("Hyderābād", 17.3617, 78.4747),
                            ("Pune", 18.5203, 73.8567),
                            ("Ahmedabad", 23.0225, 72.5714),
                            ("Sūrat", 21.1702, 72.8311),
                            ("Lucknow", 26.8500, 80.9500),
                            ("Jaipur", 26.9000, 75.8000),
                            ("Kanpur", 26.4499, 80.3319),
                            ("Nāgpur", 21.1497, 79.0806),
                            ("Vishākhapatnam", 17.7042, 83.2978),
                            ("Indore", 22.7167, 75.8472),
                        ]

        self.income = [
                        (10, 50),
                        (50, 150),
                        (100, 500),
                        (500, 2000),
                        (1000, 5000),
                        (5000, 25000),
                        (20000, 100000)
                    ]
        
        self.hours = [
                        (7,10),
                        (12,14),
                        (18,24),
                        (0,24)
                    ]

        self.device =[
                        "android_13_pixel7",
                        "android_10_oneplus",
                        "ios_17_iphone15",
                        "ios_16_iphone14",
                        "web_safari",
                        "web_edge",
                        "web_opera",
                        "windows_11_chrome",
                        "macos_ventura_safari",
                        "linux_ubuntu_firefox"
                    ]

        if set_seed is not None:
            seed(set_seed)
            Faker.seed(set_seed)

    def create_user(self):
        for i in range(0,self.n):
            city,lat,long = choice(self.cities)
            min_spend,max_spend = choice(self.income)
            peak_hours = choice(self.hours)
            devices =  choices(self.device,k=randint(1,3))
            preferred_merchants = []
            home_lat,home_lon = noise_to_dist_adder(lat,long,km_radius=5)#this is done to show movement arround\
                                                                         #the city
            self.users[i+1] = {
                                "user_id": i+1,
                                "name": faker.name(),
                                "home_city": city,
                                "home_base": (round(home_lat, 6), round(home_lon, 6)),
                                "spend_min": min_spend,
                                "spend_max": max_spend,
                                "peak_hours": peak_hours,
                                "devices": devices,
                                "preferred_merchants": preferred_merchants,
                                "recent_timestamps": []
                            }
    #come back
    def give_merchant(self,merchant_ids):
        for i in self.users.values():
            n = randint(3, min(8, max(3, len(merchant_ids))))
            i['preferred_merchants'] = sample(merchant_ids,k=n)

    def whale_assigner(self):
        'add weight to simulate higher spender'
        weights = []
        for i in self.users.values():
            a = random() + (0.5 if i['spend_max']>5000 else 0)
            weights.append(a)
        uid = choices(list(self.users.keys()),weights=weights,k=1)[0]
        return self.users[uid]
    

class Merchantmananger(Userprofile):
    def __init__(self, n_merchants=50, cities=None, set_seed=None):
        super().__init__(n_merchants, cities, set_seed)
        self.n = n_merchants
        self.merchants = {}
        self.categorys = {
                        "food": (30, 800),
                        "grocery": (50, 6000),
                        "transport": (20, 2000),
                        "shopping": (200, 15000),
                        "travel": (500, 50000),
                        "utilities": (100, 20000),
                        "entertainment": (100, 5000),
                    }

    def creat_mechant(self):
        for i in range(0, self.n):
            key = choice(list(self.categorys.keys()))
            cmin,cmax = self.categorys[key]
            city,lat,long = choice(self.cities)
            adlat,adlong= noise_to_dist_adder(lat=lat,lon=long,km_radius=15)
            self.merchants[i+1] = {
                "merchant_id": i+1,
                "name": faker.company(),
                "category": key,
                "amount_min": cmin,
                "amount_max": cmax,
                "base_city": city,
                "location": (round(adlat, 6), round(adlong, 6)),
            }

    def set_lover_merchant(self,user_profile):
        'sets prefered merchant'
        if user_profile['prepreferred_merchants'] and random()<0.7:
            a = choice(user_profile['prepreferred_merchants'])
            return self.merchants[a]
        else:
            return self.merchants[choice(list(self.merchants.keys()))]

class FraudSetter:
    def __init__(self, distance_threshold=50, velocity_threshold=5, night_penalty=1, setseed=None):
        self.distance_threshold = distance_threshold
        self.velocity_threshold = velocity_threshold
        self.night_penalty = night_penalty
        if setseed is not None:
            seed(setseed)
    
    def score(self,compare_data,user_profile):
        score = 0
        reasons = []
        if compare_data["device_id"] not in user_profile["devices"]:
            score += 2
            reasons.append("new_device")

        user_lat, user_lon = user_profile["home_base"]
        cp_lat, cp_lon = compare_data["geo_location"]
        dist = dis_calc_in_km(user_lat, user_lon, cp_lat, cp_lon)
        if dist > self.distance_threshold_km:
            score += 2
            reasons.append(f"far_location_{int(dist)}km")

        if compare_data["amount"] > user_profile["spend_max"] * 2:
            score += 2
            reasons.append("amount_spike")

        a = datetime.fromisoformat(compare_data["timestamp"].replace("Z", "+00:00"))
        hour = a.hour
        ph_start, ph_end = user_profile["peak_hours"]
        if ph_start <= ph_end:
            active = ph_start <= hour <= ph_end
        else:
            active = hour >= ph_start or hour <= ph_end
        if not active:
            score += self.night_penalty
            reasons.append("off_hours")
        one_min_ago = a - timedelta(minutes=1)
        recent_count = sum(1 for r in recent if r >= one_min_ago)
        recent = user_profile.get("recent_timestamps", [])
        if recent_count >= self.velocity_threshold:
            score += 2
            reasons.append("high_velocity")

        return score, reasons

class TransactionGenerator:
    def __init__(self,user_mgr:Userprofile,merchant_mgr:Merchantmananger,\
                 fraud_engineer:FraudSetter,setseed = None):
        self.user_obj= user_mgr
        self.merchant_obj = merchant_mgr
        self.fraud_obj = fraud_engineer
        if setseed is not None:
            seed(setseed)

    def generate(self):
        user = self.user_obj.whale_assigner()
        merchant = self.merchant_obj.set_lover_merchant(user)
        ph_start, ph_end = user['peak_hours']
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        
        if random.random() < 0.8:
            if ph_start <= ph_end:
                hour = randint(ph_start,ph_end)
            else:
                hours = list(range(ph_start,24)+list(range(0,ph_end+1)))
                hour = choice(hours)
            minu = randint(0,59)
            sec  = randint(0,59)
            ts = now.replace(hour=hour,minute=minu,second=sec)
        else:
            ts = now 
        
        bust = random()<0.6
        
        if  random()<0.03:
            device = choice(
                        [
                        "android_12_pixel", "android_11_samsung", "ios_15_iphone13",
                        "ios_14_iphone11", "web_chrome", "web_firefox", "linux_firefox"
                        ]
                    )
        else:
            device = choice(self.user_obj.device)

        if random.random() < 0.03:
            other = choice(self.user_obj.cities)
            tx_lat,tx_lon = noise_to_dist_adder(other[1],other[2],km_radius=5)
        else:
            tx_lat,tx_lon = noise_to_dist_adder(user['home_base'][0],user['home_base'][1],km_radius=15)

        base_min = max(user["spend_min"], merchant["amount_min"])
        base_max = min(user["spend_max"], merchant["amount_max"])
        if base_min >= base_max:
            amount = round(random.uniform(1, base_max * 1.1 + 10), 2)
        else:
            p = random()
            if p<0.6:
                amount = round(uniform(base_min,(base_min + base_max)/2),2)
            elif p<0.95:
                amount = round(uniform((base_min + base_max)/2,base_max),2)
            else:
                amount = round(random.uniform(base_max,base_max*5),2) 
        tx = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "merchant_id": merchant["merchant_id"],
            "amount": amount,
            "timestamp": ts.isoformat().replace("+00:00", "Z"),
            "geo_location": [round(tx_lat, 6), round(tx_lon, 6)],
            "device_id": device,
            "merchant_category": merchant["category"],
            "city": merchant["base_city"],
        }

        recent = user.get("recent_timestamps", [])
        now_dt = datetime.fromisoformat(tx["timestamp"].replace("Z", "+00:00"))
        recent = [r for r in recent if r >= now_dt - timedelta(minutes=10)]
        recent.append(now_dt)
        user["recent_timestamps"] = recent

        score, reasons = self.fraud_engine.score(tx, user)
        tx["fraud_score"] = score
        tx["fraud_reasons"] = reasons
        tx["is_fraud"] = 1 if score >= 2 else 0
        user_lat, user_lon = user["home_base"]
        tx["distance_from_home_km"] = round(dis_calc_in_km(user_lat, user_lon, tx_lat, tx_lon), 2)

        result = [tx]

        if bust:
            for i in range(randint(2,4)):
                b = dict(tx)
                b['transaction_id'] = (now_dt +timedelta(seconds=random.randint(1, 30))).isoformat().replace("+00:00", "Z")
                b["amount"] = round(max(1.0, b["amount"] * random.uniform(0.5, 1.5)), 2)
                if random.random() < 0.2:
                    b["device_id"] = random.choice(["android_11_samsung", "web_chrome", "ios_15_iphone13"])
                score2, reasons2 = self.fraud_engine.score(b, user)
                b["fraud_score"] = score2
                b["fraud_reasons"] = reasons2
                b["is_fraud"] = 1 if score2 >= 2 else 0
                result.append(b)
        return result
    
class Simulator:
    def __init__(self,args):
        self.args = args
        if args.seed is not None:
            seed(args.seed)
            Faker.seed(args.seed)

        self.user_mgr = Userprofile(n_users=args.num_users, seed=args.seed)
        self.user_mgr.create_user()
        self.merchant_mgr = Merchantmananger(n_merchants=args.num_merchants, seed=args.seed)
        self.merchant_mgr.creat_mechant()
        self.user_mgr.give_merchant(list(self.merchant_mgr.merchants.keys()))
        self.fraud_engine = FraudSetter(distance_threshold_km=args.distance_km,
                                        velocity_threshold=args.velocity_threshold,
                                        seed=args.seed)
        self.txgen = TransactionGenerator(self.user_mgr, self.merchant_mgr, self.fraud_engine, seed=args.seed)
        self.out_file = None

        if args.out_file:
            self.out_file = open(args.out_file, "a", buffering=1)

        self.redis_client = None
        if args.redis_url:
                self.redis_client = redis.from_url(args.redis_url, decode_responses=True)

        self.stop_flag = threading.Event()


def parse_args():
    p = argparse.ArgumentParser(description="Realistic transaction simulator")
    p.add_argument("--num-users", type=int, default=300, help="Number of fake users to generate")
    p.add_argument("--num-merchants", type=int, default=60, help="Number of merchants")
    p.add_argument("--rate", type=float, default=10.0, help="Average transactions per second")
    p.add_argument("--out-file", type=str, default=None, help="Write JSONL output to this file")
    p.add_argument("--redis-url", type=str, default=None, help="Optional Redis URL to push Stream entries")
    p.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    p.add_argument("--distance-km", type=float, default=50.0, help="Distance threshold for fraud scoring (km)")
    p.add_argument("--velocity-threshold", type=int, default=5, help="Transactions/min velocity threshold")
    return p.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    sim = Simulator(args)

    def shutdown(sig, frame):
        LOG.info("Signal %s received, stopping...", sig)
        sim.stop_flag.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    sim.run() 

if __name__ == '__main__':
    main()