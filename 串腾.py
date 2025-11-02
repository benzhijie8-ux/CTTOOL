#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
串腾美化工具 - 增强版
包含每日激励话语、主题自定义、系统监控状态
"""
import os
import sys
import time
import random
import platform
import subprocess
import shutil
import signal
import math
import requests
import json
import threading
from datetime import datetime

# ==================== 自动安装依赖 ====================
try:
    import colorama
    from colorama import init, Style, Fore
except ModuleNotFoundError:
    print("正在安装 colorama...")
    os.system('pip3 install colorama')
    import colorama
    from colorama import init, Style, Fore

try:
    import psutil
except ModuleNotFoundError:
    print("正在安装 psutil...")
    os.system('pip3 install psutil')
    import psutil

init(autoreset=True)

# ==================== 全局变量 ====================
music_process = None
current_song = None
current_theme = "default"

# ==================== 主题系统 ====================
class Themes:
    # 默认主题
    default = {
        "PRIMARY": '\033[96m',      # 青色
        "SECONDARY": '\033[92m',    # 绿色
        "ACCENT": '\033[93m',       # 黄色
        "WARNING": '\033[91m',      # 红色
        "INFO": '\033[94m',         # 蓝色
        "TEXT": '\033[97m'          # 白色
    }
    
    # 暗黑主题
    dark = {
        "PRIMARY": '\033[38;2;0;255;255m',    # 青色
        "SECONDARY": '\033[38;2;0;255;0m',    # 绿色
        "ACCENT": '\033[38;2;255;255;0m',     # 黄色
        "WARNING": '\033[38;2;255;0;0m',      # 红色
        "INFO": '\033[38;2;0;0;255m',         # 蓝色
        "TEXT": '\033[38;2;255;255;255m'      # 白色
    }
    
    # 金色主题
    gold = {
        "PRIMARY": '\033[38;2;255;215;0m',    # 金色
        "SECONDARY": '\033[38;2;255;165;0m',  # 橙色
        "ACCENT": '\033[38;2;255;255;0m',     # 黄色
        "WARNING": '\033[38;2;255;69;0m',     # 红色
        "INFO": '\033[38;2;218;165;32m',      # 金色
        "TEXT": '\033[38;2;255;250;205m'      # 浅黄色
    }
    
    # 紫色主题
    purple = {
        "PRIMARY": '\033[38;2;138;43;226m',   # 蓝紫色
        "SECONDARY": '\033[38;2;147;112;219m',# 中紫色
        "ACCENT": '\033[38;2;186;85;211m',    # 中兰花紫
        "WARNING": '\033[38;2;255;0;255m',    # 洋红色
        "INFO": '\033[38;2;75;0;130m',        # 靛蓝色
        "TEXT": '\033[38;2;216;191;216m'      # 蓟色
    }

def get_theme():
    """获取当前主题"""
    return Themes.__dict__.get(current_theme, Themes.default)

def clear_screen():
    """清屏函数"""
    os.system('clear' if os.name != 'nt' else 'cls')

# ==================== 音乐系统 ====================
class MusicSystem:
    @staticmethod
    def get_playlist_songs():
        """获取歌单中的歌曲列表"""
        try:
            url = "https://api.injahow.cn/meting/?type=playlist&id=13875199712&server=netease"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                songs = response.json()
                return songs
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def play_random_song():
        """随机播放歌单中的一首歌"""
        global music_process, current_song
        
        try:
            songs = MusicSystem.get_playlist_songs()
            
            if not songs:
                return
            
            # 随机选择一首歌
            song = random.choice(songs)
            current_song = song
            
            song_url = song.get('url')
            
            if not song_url:
                return
            
            # 使用mpv播放音乐（后台播放）
            if shutil.which("mpv"):
                music_process = subprocess.Popen(
                    ["mpv", "--no-video", "--no-terminal", song_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif shutil.which("mplayer"):
                music_process = subprocess.Popen(
                    ["mplayer", "-vo", "null", song_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
        except Exception:
            pass

    @staticmethod
    def stop_music():
        """停止音乐播放"""
        global music_process
        if music_process and music_process.poll() is None:
            music_process.terminate()
            music_process.wait()

# ==================== 激励话语系统 ====================
class MotivationSystem:
    # 内置激励话语（如果API不可用时的备用）
    default_motivations = [
        "今天是你余生的第一天，让它变得有意义！",
        "每一次努力都是未来的你在向现在的你求救！",
        "代码如诗，调试如歌，坚持就是胜利！",
        "不要因为结束而哭泣，要为曾经发生而微笑！",
        "成功的秘诀就是每天进步一点点！",
        "你的潜力超乎你的想象，继续前进！",
        "每一个伟大的程序都始于一个简单的想法！",
        "错误不是失败，而是学习的机会！",
        "保持好奇心，世界因你而不同！",
        "今天的努力，是明天的实力！"
    ]
    
    @staticmethod
    def get_daily_motivation():
        """获取每日激励话语"""
        try:
            # 使用DeepSeek API获取激励话语
            # 注意：这里需要您提供有效的API密钥
            api_key = "sk-6bc3be67d7d344988b4b4e198c833a83"  # 请确保这是有效的API密钥
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个励志助手，请提供一句简短有力的每日激励话语。"},
                    {"role": "user", "content": "请给我一句今日激励话语，适合程序员，简短有力。"}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(
                "https://api.deepseek.com串腾chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                motivation = result["choices"][0]["message"]["content"].strip()
                return motivation
            else:
                # API失败时使用内置话语
                return random.choice(MotivationSystem.default_motivations)
                
        except Exception:
            # 异常时使用内置话语
            return random.choice(MotivationSystem.default_motivations)

# ==================== 系统监控系统 ====================
class SystemMonitor:
    @staticmethod
    def get_system_status():
        """获取系统状态信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            return {
                "cpu": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used": memory_used,
                "memory_total": memory_total,
                "disk_percent": disk_percent,
                "disk_used": disk_used,
                "disk_total": disk_total
            }
        except Exception:
            # 如果psutil不可用，返回默认值
            return {
                "cpu": 0,
                "memory_percent": 0,
                "memory_used": 0,
                "memory_total": 0,
                "disk_percent": 0,
                "disk_used": 0,
                "disk_total": 0
            }

# ==================== 清理系统 ====================
class CleanupSystem:
    @staticmethod
    def cleanup_system():
        """执行系统清理"""
        try:
            # 清理临时文件
            temp_dirs = [
                "/tmp",
                "/data/data/com.termux/files/usr/tmp",
                os.path.expanduser("~/.cache")
            ]
            
            cleaned_files = 0
            cleaned_size = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                cleaned_files += 1
                                cleaned_size += file_size
                            except:
                                pass
            
            # 转换为MB
            cleaned_size_mb = cleaned_size / (1024**2)
            
            return cleaned_files, cleaned_size_mb
            
        except Exception as e:
            return 0, 0

# ==================== 简洁动画系统 ====================
class SimpleAnimations:
    @staticmethod
    def show_logo(theme):
        """显示简洁LOGO"""
        logo = [
            "==============================================",
            "                                            ",
            "             串腾美化工具 v5.0              ",
            "                 🎵 增强版 🎵              ",
            "=============================================="
        ]
        
        for line in logo:
            if "串腾" in line:
                color = theme["PRIMARY"]
            elif "增强" in line:
                color = theme["ACCENT"]
            elif "====" in line:
                color = theme["SECONDARY"]
            else:
                color = theme["TEXT"]
            print(color + line)
            time.sleep(0.02)

    @staticmethod
    def simple_loader(text="加载中", duration=1.0, theme=None):
        """简洁加载动画"""
        if theme is None:
            theme = get_theme()
            
        frames = ["-", "\\", "|", "/"]
        
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            progress = min(1.0, elapsed / duration)
            
            spin_char = frames[int(time.time() * 4) % len(frames)]
            percent = int(progress * 100)
            
            sys.stdout.write(f"\r{spin_char} {theme['PRIMARY']}{text} {percent}%")
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(f"\r{theme['SECONDARY']}✓ {text} 完成")

# ==================== 增强UI组件 ====================
class EnhancedUI:
    @staticmethod
    def print_status_box(theme):
        """显示状态框（激励话语、系统状态、当前歌曲）"""
        print(f"{theme['SECONDARY']}┌{'─' * 58}┐")
        
        # 每日激励话语
        motivation = MotivationSystem.get_daily_motivation()
        motivation_line = f"│ {theme['ACCENT']}💫 今日激励: {motivation}"
        print(f"{theme['SECONDARY']}{motivation_line}{' ' * (58 - len(motivation) - 13)}{theme['SECONDARY']}│")
        
        # 系统状态
        status = SystemMonitor.get_system_status()
        cpu_line = f"│ {theme['INFO']}🖥️  CPU: {status['cpu']:.1f}%"
        memory_line = f"│ {theme['INFO']}💾 内存: {status['memory_used']:.1f}G/{status['memory_total']:.1f}G ({status['memory_percent']:.1f}%)"
        disk_line = f"│ {theme['INFO']}💿 磁盘: {status['disk_used']:.1f}G/{status['disk_total']:.1f}G ({status['disk_percent']:.1f}%)"
        
        print(f"{theme['SECONDARY']}{cpu_line}{' ' * (58 - len(cpu_line) + 25)}{theme['SECONDARY']}│")
        print(f"{theme['SECONDARY']}{memory_line}{' ' * (58 - len(memory_line) + 20)}{theme['SECONDARY']}│")
        print(f"{theme['SECONDARY']}{disk_line}{' ' * (58 - len(disk_line) + 20)}{theme['SECONDARY']}│")
        
        # 当前播放歌曲
        global current_song
        if current_song:
            song_name = current_song.get('name', '未知歌曲')
            artist = current_song.get('artist', '未知艺术家')
            song_line = f"│ {theme['PRIMARY']}🎵 正在播放: {song_name} - {artist}"
            if len(song_line) > 70:
                song_line = song_line[:67] + "..."
            print(f"{theme['SECONDARY']}{song_line}{' ' * (58 - len(song_line) + 25)}{theme['SECONDARY']}│")
        
        print(f"{theme['SECONDARY']}└{'─' * 58}┘")

    @staticmethod
    def print_enhanced_menu(menu_items, theme):
        """显示增强菜单"""
        # 系统信息
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{theme['TEXT']}系统时间: {current_time}")
        print(f"{theme['PRIMARY']}串腾美化工具 - 增强版 | 当前主题: {current_theme}")
        
        # 显示状态框
        print()
        EnhancedUI.print_status_box(theme)
        print()
        
        # 核心功能
        print(f"{theme['SECONDARY']}【核心功能】")
        for i in range(0, min(15, len(menu_items))):
            num = i + 1
            item = menu_items[i]
            print(f"  {theme['SECONDARY']}{num:2d}. {item}")
        
        # 辅助功能
        print(f"\n{theme['INFO']}【辅助功能】")
        for i in range(15, min(30, len(menu_items))):
            num = i + 1
            item = menu_items[i]
            print(f"  {theme['INFO']}{num:2d}. {item}")
        
        # 其他功能
        if len(menu_items) > 30:
            print(f"\n{theme['ACCENT']}【其他功能】")
            for i in range(30, len(menu_items)):
                num = i + 1
                item = menu_items[i]
                print(f"  {theme['ACCENT']}{num:2d}. {item}")
        
        print(f"\n{theme['PRIMARY']}" + "=" * 50)
        print(f"{theme['TEXT']}输入 0 退出程序")

# ==================== 系统核心 ====================
def enhanced_startup():
    """增强启动序列"""
    clear_screen()
    theme = get_theme()
    
    # 显示LOGO
    print("\n")
    SimpleAnimations.show_logo(theme)
    time.sleep(0.5)
    
    # 系统加载
    print(f"\n{theme['PRIMARY']}正在启动串腾美化工具...\n")
    SimpleAnimations.simple_loader("系统初始化", 0.5, theme)
    SimpleAnimations.simple_loader("加载核心模块", 0.4, theme)
    
    # 启动音乐播放（在后台线程中）
    print(f"{theme['PRIMARY']}启动音乐系统...")
    music_thread = threading.Thread(target=MusicSystem.play_random_song)
    music_thread.daemon = True
    music_thread.start()
    
    SimpleAnimations.simple_loader("准备界面", 0.3, theme)
    
    time.sleep(0.2)

# ==================== 主程序 ====================
def main():
    """主程序"""
    try:
        # 增强启动序列
        enhanced_startup()
        
        # 显示主菜单
        show_main_menu()
        
    except KeyboardInterrupt:
        theme = get_theme()
        print(f"\n{theme['SECONDARY']}感谢使用串腾美化工具！")
    except Exception as e:
        theme = get_theme()
        print(f"{theme['WARNING']}系统错误: {e}")
    finally:
        # 确保程序退出时停止音乐
        MusicSystem.stop_music()

def show_main_menu():
    """显示主菜单"""
    # 完整功能列表（新增了主题切换和系统清理）
    menu_items = [
        "第一次使用，必须先创建文件夹",
        "uexp全自动美化", 
        "全自动制作播报等",
        "全自动制作地铁",
        "全自动uexp手持an完美头",
        "全自动制作广角", 
        "全自动制作天线",
        "lo美化制作",
        "uexp全部类型",
        "uexp伪实体", 
        "大厅完美头2",
        "自动修改宠物动作",
        "自动改八场",
        "全自动制作八场", 
        "免root输出",
        "py转配料表",
        "加注释", 
        "全自动偷配置",
        "修改背景",
        "自动删除小包", 
        "系统公告",
        "MK14枪械功能",
        "txtpy格式转换",
        "大厅手持火焰刀", 
        "进入樱花吹雪",
        "半自动写配置",
        "神秘功能",
        "检查配置", 
        "播放音乐",
        "地铁美化",
        "打包",
        "零战备+入场", 
        "设置快捷指令",
        "切换主题",           # 新增功能
        "一键清理系统"        # 新增功能
    ]
    
    while True:
        clear_screen()
        theme = get_theme()
        
        # 显示增强菜单
        EnhancedUI.print_enhanced_menu(menu_items, theme)
        print()
        
        # 用户输入
        try:
            choice = input(f"{theme['PRIMARY']}请输入选项: ").strip()
            
            if choice == '0':
                print(f"\n{theme['SECONDARY']}感谢使用串腾美化工具！")
                break
            elif choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(menu_items):
                    execute_command(choice, menu_items[choice_num-1], theme)
                else:
                    print(f"{theme['WARNING']}无效选项！")
                    time.sleep(1)
            else:
                print(f"{theme['WARNING']}请输入数字！")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{theme['SECONDARY']}系统关闭...")
            break
        except ValueError:
            print(f"{theme['WARNING']}输入错误！")
            time.sleep(1)

def execute_command(choice, command_name, theme):
    """执行命令"""
    global current_theme
    
    # 特殊功能处理
    if choice == "34":  # 切换主题
        themes = ["default", "dark", "gold", "purple"]
        current_index = themes.index(current_theme)
        current_theme = themes[(current_index + 1) % len(themes)]
        print(f"{theme['PRIMARY']}已切换到 {current_theme} 主题")
        time.sleep(1)
        return
        
    elif choice == "35":  # 一键清理系统
        print(f"\n{theme['INFO']}正在执行系统清理...")
        cleaned_files, cleaned_size = CleanupSystem.cleanup_system()
        print(f"{theme['SECONDARY']}清理完成！")
        print(f"{theme['INFO']}清理了 {cleaned_files} 个文件，释放了 {cleaned_size:.2f} MB 空间")
        input(f"\n{theme['PRIMARY']}按回车继续...")
        return
    
    # 原有命令映射
    command_map = {
        '1': "./自动创建文件夹",
        '2': "./uexp载具 && ./uexp", 
        '3': "./全自动美化",
        '4': "./自动四类",
        '5': "./自动修改地铁枪皮dat",
        '6': "./手持", 
        '7': "./广角",
        '8': "./天线", 
        '9': "./美化",
        '10': "./uexp载具",
        '11': "./uexp", 
        '12': "./偷配置",
        '13': "./大厅完美头",
        '14': "./地铁偷配置", 
        '15': "./播报偷配置",
        '16': "./38",
        '17': "./写地铁配置", 
        '18': "./半自动写配置",
        '19': "./Py转配料表", 
        '20': "./py装",
        '21': "./抓小包", 
        '22': "./检查配置",
        '23': "./打包解包",
        '24': "./六合一查找", 
        '25': "./输出",
        '26': "./网易云反", 
        '27': "./自动添加水印",
        '28': "./注释1", 
        '29': "bash 启动.sh",
        '30': "python 黄色", 
        '31': "./2.0",
        '32': "./动作", 
        '33': "./37"
    }
    
    cmd = command_map.get(choice)
    
    if not cmd:
        print(f"{theme['WARNING']}功能未实现: {command_name}")
        time.sleep(1)
        return
    
    # 执行前的提示
    print(f"\n{theme['INFO']}准备执行: {command_name}")
    SimpleAnimations.simple_loader(f"启动 {command_name}", 0.8, theme)
    
    try:
        # 执行命令
        print(f"\n{theme['SECONDARY']}开始执行...")
        result = subprocess.run(cmd, shell=True)
        if result.returncode == 0:
            print(f"{theme['SECONDARY']}执行完成！")
        else:
            print(f"{theme['WARNING']}命令执行完成")
    except Exception as e:
        print(f"{theme['WARNING']}执行错误: {e}")
    
    input(f"\n{theme['PRIMARY']}按回车继续...")

if __name__ == "__main__":
    main()