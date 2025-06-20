# rules.py
# 全局在贷笔数

def get_max_available_loan_count(user_id):
    global_loan_dict = {
        "user_001": 2,
        "user_002": 1,
        "user_003": 3
    }
    return global_loan_dict.get(user_id, 0)

def check_min_age(info, fea, score):
    # 年龄<18拒绝，返回1，否则0
    return 1 if info.get("age", 0) < 18 else 0

def check_income(info, fea, score):
    # 收入<3000拒绝，返回1，否则0
    return 1 if fea.get("income", 0) < 3000 else 0

def check_blacklist(info, fea, score):
    # user_id在黑名单拒绝，返回1，否则0
    return 1 if info.get("user_id", "") in ["black_user_001", "black_user_002"] else 0

def check_score(info, fea, score):
    # 模型分<0.7拒绝，返回1，否则0
    return 1 if score.get("main_score", 0) < 0.7 else 0

def check_callback(info, fea, score):
    # 命中回捞规则时返回1（表示可回捞=通过），否则返回0
    return 1 if fea.get("user_level", "") == "VIP" else 0

def check_loan_count(info, fea, score):
    # 当前在贷笔数>=最大可贷拒绝，返回1，否则0
    user_id = info.get("user_id", "")
    # 当前在贷笔数
    max_loan = fea.get("max_loan_count", 1)
    # 最大可在贷笔数
    current_loan = get_max_available_loan_count(user_id)
    return 1 if current_loan <= max_loan else 0

def get_marketing_tag(main_score):
    if main_score >= 0.8:
        return "高分用户"
    elif main_score >= 0.6:
        return "中分用户"
    else:
        return "普通用户"