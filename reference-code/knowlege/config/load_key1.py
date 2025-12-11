import json
import os
import getpass
import sys

try:
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("警告: dashscope 模块未安装，将无法配置API密钥到dashscope模块")
    print("请运行 'pip install dashscope' 安装该模块")


def load_key():
    """
    加载和配置阿里云通义千问API密钥
    工作流程：
    1. 尝试从Key.json文件读取API密钥
    2. 如果文件存在且包含密钥，加载到环境变量
    3. 如果文件不存在，提示用户输入密钥并保存
    4. 将密钥配置到dashscope模块
    """
    key_file_path = "../Key.json"
    
    # 尝试从文件读取密钥
    if os.path.exists(key_file_path):
        try:
            with open(key_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'api_key' in data and data['api_key']:
                    api_key = data['api_key']
                    print("从文件中加载API密钥成功")
                else:
                    print("文件中未找到有效的API密钥")
                    api_key = get_user_input()
                    save_key_to_file(api_key, key_file_path)
        except json.JSONDecodeError:
            print("密钥文件格式错误，重新输入API密钥")
            api_key = get_user_input()
            save_key_to_file(api_key, key_file_path)
        except Exception as e:
            print(f"读取密钥文件时发生错误: {e}")
            api_key = get_user_input()
            save_key_to_file(api_key, key_file_path)
    else:
        print("密钥文件不存在，需要输入API密钥")
        api_key = get_user_input()
        save_key_to_file(api_key, key_file_path)
    
    # 设置环境变量
    os.environ['DASHSCOPE_API_KEY'] = api_key
    print("已将API密钥设置到环境变量")
    
    # 配置dashscope模块
    if DASHSCOPE_AVAILABLE:
        dashscope.api_key = api_key
        print("已将API密钥配置到dashscope模块")
    else:
        print("dashscope模块不可用，跳过模块配置")
    
    return api_key


def get_user_input():
    """安全获取用户输入的API密钥"""
    print("请输入您的阿里云通义千问API密钥:")
    api_key = getpass.getpass("API密钥: ")
    if not api_key:
        print("API密钥不能为空，请重新输入")
        return get_user_input()
    return api_key


def save_key_to_file(api_key, file_path):
    """将API密钥保存到JSON文件"""
    try:
        data = {'api_key': api_key}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"API密钥已保存到 {file_path}")
    except Exception as e:
        print(f"保存密钥文件时发生错误: {e}")
        # 如果保存失败，询问用户是否重试
        retry = input("是否重试保存? (y/n): ").lower().strip()
        if retry == 'y':
            save_key_to_file(api_key, file_path)


def main():
    """主程序入口"""
    print("=" * 50)
    print("阿里云通义千问API密钥配置工具")
    print("=" * 50)
    
    try:
        api_key = load_key()
        print("\nAPI密钥配置完成!")
        print(f"密钥长度: {len(api_key)} 字符")
        print("现在您可以使用阿里云通义千问API了")
        
        # 验证配置是否成功
        if DASHSCOPE_AVAILABLE:
            print("\n验证dashscope配置...")
            try:
                # 简单测试API密钥格式（不实际调用API）
                if api_key.startswith('sk-') and len(api_key) > 10:
                    print("API密钥格式检查通过")
                else:
                    print("警告: API密钥格式可能不正确")
            except Exception as e:
                print(f"验证过程中出现错误: {e}")
        
        print("\n环境变量 DASHSCOPE_API_KEY 已设置")
        print("dashscope模块已配置（如果可用）")
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序执行过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()