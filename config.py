# config.py
class Config:
    # 是否启用分流实验
    ENABLE_EXPERIMENT = True
    
    # 分流实验组及流量占比
    EXPERIMENTS = [
        {"name": "A", "ratio": 0.4},
        {"name": "B", "ratio": 0.6}
    ]
    # 未启用分流实验时的默认流名
    DEFAULT_FLOW = "base"

    # 规则集配置（每个规则集每个流独立配置）
    RULE_SETS = {
        "access_rules": {
            "base": [
                {"code": "ACC001", "func": "check_min_age"},
                {"code": "ACC002", "func": "check_income"}
            ],
            "A": [
                {"code": "ACC_A01", "func": "check_min_age"},
                {"code": "ACC_A02", "func": "check_income"}
            ],
            "B": [
                {"code": "ACC_B01", "func": "check_min_age"},
                {"code": "ACC_B02", "func": "check_income"}
            ]
        },
        "fraud_rules": {
            "base": [
                {"code": "FRA001", "func": "check_blacklist"}
            ],
            "A": [
                {"code": "FRA_A01", "func": "check_blacklist"}
            ],
            "B": [
                {"code": "FRA_B01", "func": "check_blacklist"}
            ]
        },
        "model_rules": {
            "base": [
                {"code": "MOD001", "func": "check_score"}
            ],
            "A": [
                {"code": "MOD_A01", "func": "check_score"}
            ],
            "B": [
                {"code": "MOD_B01", "func": "check_score"}
            ]
        },
        "callback_rules": {
            "base": [
                {"code": "CALL001", "func": "check_callback"}
            ],
            "A": [
                {"code": "CALL_A01", "func": "check_callback"}
            ],
            "B": [
                {"code": "CALL_B01", "func": "check_callback"}
            ]
        },
        "loan_rules": {
            "base": [
                {"code": "LOAN001", "func": "check_loan_count"}
            ],
            "A": [
                {"code": "LOAN_A01", "func": "check_loan_count"}
            ],
            "B": [
                {"code": "LOAN_B01", "func": "check_loan_count"}
            ]
        }
    }