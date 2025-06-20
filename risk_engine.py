# risk_engine.py
import hashlib
from config import Config
import rules

class RiskDecisionEngine:
    def __init__(self):
        # 自动加载 rules.py 中所有非私有函数
        self.func_map = {name: func for name, func in vars(rules).items() if callable(func) and not name.startswith("_")}
        print("已加载以下规则函数:", list(self.func_map.keys()))

    def get_flowname(self, user_id):
        if not Config.ENABLE_EXPERIMENT:
            return Config.DEFAULT_FLOW, ""
        h_val = hashlib.sha256(user_id.encode()).hexdigest()
        h = int(h_val, 16) % 10000 / 10000.0
        ratio_sum = 0
        for exp in Config.EXPERIMENTS:
            ratio_sum += exp["ratio"]
            if h < ratio_sum:
                return exp["name"], h
        return Config.DEFAULT_FLOW, h

    def make_decision(self, info, fea, score):
        flowname, hash_value = self.get_flowname(info["user_id"])
        global_loan_count = rules.get_max_available_loan_count(info["user_id"])
        result = {
            "order_id": info["order_id"],
            "user_id": info["user_id"],
            "decision": "通过",
            "flowname": flowname,
            "callback_name": "",
            "hit_fea": [],
            "first_hit_fea": "",
            "isRulePass": 1,  # 1为通过，0为未通过
            "投放标签": "",
            "最大可在贷笔数": global_loan_count,
            "hash_value": hash_value if Config.ENABLE_EXPERIMENT else "",
            "debug_log": []  # 新增调试日志
        }
        all_hits = []
        first_hit = ""
        is_rule_pass = 1  # 1为通过，0为未通过
        callback_name = ""
        access_fraud_reject = False
        callback_hit = False
        callback_code = ""
        callback_passed = False  # 标记是否回捞通过
        # 决策顺序
        rule_seq = ["access_rules", "fraud_rules", "model_rules", "callback_rules", "loan_rules"]
        for ruleset in rule_seq:
            # 支持规则集fallback到base
            rules_list = Config.RULE_SETS[ruleset].get(flowname) or Config.RULE_SETS[ruleset].get("base", [])
            for rule in rules_list:
                func = self.func_map[rule["func"]]
                # 支持规则参数扩展
                params = rule.get("params", {})
                try:
                    ret = func(info, fea, score, **params) if params else func(info, fea, score)
                except Exception as e:
                    result["debug_log"].append(f"规则{rule['code']}执行异常:{e}")
                    ret = 0  # 默认通过
                result["debug_log"].append(f"规则集:{ruleset}, 规则:{rule['code']}, 返回:{ret}")
                if ruleset == "callback_rules":
                    if ret == 1 and result["decision"] == "拒绝" and result["isRulePass"] == 1:
                        callback_hit = True
                        callback_code = rule["code"]
                        result["decision"] = "通过"
                        result["callback_name"] = callback_code
                        callback_passed = True
                else:
                    if ret == 1:  # 1为拒绝
                        all_hits.append(rule["code"])
                        if not first_hit:
                            first_hit = rule["code"]
                        if ruleset in ["access_rules", "fraud_rules"]:
                            access_fraud_reject = True
                        result["decision"] = "拒绝"  # 命中任何非回捞规则都置为拒绝
            # loan_rules命中拒绝，决策必须为拒绝
            if ruleset == "loan_rules" and any(
                (self.func_map[rule["func"]](info, fea, score, **rule.get("params", {})) if rule.get("params") else self.func_map[rule["func"]](info, fea, score)) == 1
                for rule in rules_list):
                result["decision"] = "拒绝"
        # isRulePass 逻辑修正
        result["isRulePass"] = 0 if access_fraud_reject else 1
        # 投放标签
        result["投放标签"] = rules.get_marketing_tag(score.get("main_score", 0))
        result["hit_fea"] = all_hits
        result["first_hit_fea"] = first_hit
        return result

if __name__ == "__main__":
    engine = RiskDecisionEngine()
    # 测试样例
    test_cases = [
        {
            "info": {"order_id": "O1", "user_id": "user_001", "age": 22},
            "fea": {"income": 7000, "user_level": "VIP", "max_loan_count": 3},
            "score": {"main_score": 0.85}
        },
        {
            "info": {"order_id": "O2", "user_id": "user_002", "age": 17},
            "fea": {"income": 4000, "user_level": "普通", "max_loan_count": 2},
            "score": {"main_score": 0.65}
        },
        {
            "info": {"order_id": "O3", "user_id": "user_003", "age": 25},
            "fea": {"income": 2000, "user_level": "VIP", "max_loan_count": 3},
            "score": {"main_score": 0.55}
        }
    ]
    for case in test_cases:
        res = engine.make_decision(case["info"], case["fea"], case["score"])
        print(res)