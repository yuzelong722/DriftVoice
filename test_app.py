#!/usr/bin/env python3
"""
测试研声漂流应用的基本功能
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_home_page():
    """测试首页"""
    print("测试首页...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ 首页访问成功")
            return True
        else:
            print(f"✗ 首页访问失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 首页访问异常：{e}")
        return False

def test_create_question_page():
    """测试发布问题页面"""
    print("测试发布问题页面...")
    try:
        response = requests.get(f"{BASE_URL}/question/create")
        if response.status_code == 200:
            print("✓ 发布问题页面访问成功")
            return True
        else:
            print(f"✗ 发布问题页面访问失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 发布问题页面访问异常：{e}")
        return False

def test_pending_questions_page():
    """测试待回应问题页面"""
    print("测试待回应问题页面...")
    try:
        response = requests.get(f"{BASE_URL}/questions/pending")
        if response.status_code == 200:
            print("✓ 待回应问题页面访问成功")
            return True
        else:
            print(f"✗ 待回应问题页面访问失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 待回应问题页面访问异常：{e}")
        return False

def test_my_messages_page():
    """测试我的回信页面"""
    print("测试我的回信页面...")
    try:
        response = requests.get(f"{BASE_URL}/my/messages")
        if response.status_code == 200:
            print("✓ 我的回信页面访问成功")
            return True
        else:
            print(f"✗ 我的回信页面访问失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 我的回信页面访问异常：{e}")
        return False

def test_experience_library_page():
    """测试经验库页面"""
    print("测试经验库页面...")
    try:
        response = requests.get(f"{BASE_URL}/experience")
        if response.status_code == 200:
            print("✓ 经验库页面访问成功")
            return True
        else:
            print(f"✗ 经验库页面访问失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 经验库页面访问异常：{e}")
        return False

def test_api_pending_questions():
    """测试API：获取待回应问题"""
    print("测试API：获取待回应问题...")
    try:
        response = requests.get(f"{BASE_URL}/api/questions/pending")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API调用成功，返回{len(data)}个问题")
            return True
        else:
            print(f"✗ API调用失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API调用异常：{e}")
        return False

def test_api_create_reply():
    """测试API：创建回复"""
    print("测试API：创建回复...")
    try:
        # 首先获取一个问题
        response = requests.get(f"{BASE_URL}/api/questions/pending")
        if response.status_code == 200:
            questions = response.json()
            if len(questions) > 0:
                question_id = questions[0]['id']
                
                # 创建回复
                reply_data = {
                    "content": "这是一个测试回复。我建议你可以尝试和导师沟通。",
                    "response_style": "我提供一个现实建议"
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/questions/{question_id}/replies",
                    json=reply_data
                )
                
                if response.status_code == 201:
                    print("✓ 回复创建成功")
                    return True
                else:
                    print(f"✗ 回复创建失败，状态码：{response.status_code}")
                    return False
            else:
                print("✗ 没有可用的问题来测试回复创建")
                return False
        else:
            print(f"✗ 无法获取问题列表来测试回复创建，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API调用异常：{e}")
        return False

def test_api_thank_reply():
    """测试API：感谢回复"""
    print("测试API：感谢回复...")
    try:
        # 首先获取一个问题及其回复
        response = requests.get(f"{BASE_URL}/api/questions/pending")
        if response.status_code == 200:
            questions = response.json()
            if len(questions) > 0:
                question_id = questions[0]['id']
                
                # 获取问题详情和回复
                response = requests.get(f"{BASE_URL}/api/questions/{question_id}")
                if response.status_code == 200:
                    question_data = response.json()
                    if len(question_data['replies']) > 0:
                        reply_id = question_data['replies'][0]['id']
                        
                        # 感谢回复
                        response = requests.post(f"{BASE_URL}/api/replies/{reply_id}/thank")
                        
                        if response.status_code == 200:
                            print("✓ 感谢回复成功")
                            return True
                        else:
                            print(f"✗ 感谢回复失败，状态码：{response.status_code}")
                            return False
                    else:
                        print("✗ 该问题没有回复，无法测试感谢功能")
                        return False
                else:
                    print(f"✗ 无法获取问题详情来测试感谢功能，状态码：{response.status_code}")
                    return False
            else:
                print("✗ 没有可用的问题来测试感谢功能")
                return False
        else:
            print(f"✗ 无法获取问题列表来测试感谢功能，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API调用异常：{e}")
        return False

def test_api_experiences():
    """测试API：获取经验库"""
    print("测试API：获取经验库...")
    try:
        response = requests.get(f"{BASE_URL}/api/experiences")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API调用成功，返回{len(data)}个经验")
            return True
        else:
            print(f"✗ API调用失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API调用异常：{e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("研声漂流应用功能测试")
    print("=" * 50)
    
    results = []
    
    # 测试页面访问
    results.append(("首页", test_home_page()))
    time.sleep(0.5)
    
    results.append(("发布问题页面", test_create_question_page()))
    time.sleep(0.5)
    
    results.append(("待回应问题页面", test_pending_questions_page()))
    time.sleep(0.5)
    
    results.append(("我的回信页面", test_my_messages_page()))
    time.sleep(0.5)
    
    results.append(("经验库页面", test_experience_library_page()))
    time.sleep(0.5)
    
    # 测试API端点
    results.append(("API：获取待回应问题", test_api_pending_questions()))
    time.sleep(0.5)
    
    results.append(("API：创建回复", test_api_create_reply()))
    time.sleep(0.5)
    
    results.append(("API：感谢回复", test_api_thank_reply()))
    time.sleep(0.5)
    
    results.append(("API：获取经验库", test_api_experiences()))
    
    # 打印测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计：{passed + failed} 个测试，通过：{passed}，失败：{failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！应用运行正常。")
    else:
        print(f"\n⚠️  有{failed}个测试失败，请检查应用。")
    
    return failed == 0

if __name__ == "__main__":
    run_all_tests()