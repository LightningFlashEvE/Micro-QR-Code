"""
Micro QR Code 生成器配置文件

支持自定义默认参数和应用程序设置。
"""

import json
import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        # GUI 设置
        "gui": {
            "window_width": 600,
            "window_height": 760,
            "max_preview_size": 320,
            "base_qr_size": 30
        },
        
        # 默认参数
        "defaults": {
            "format": "png",
            "scale": 1,
            "border": 1,
            "error_correction": "L"
        },
        
        # 文件路径设置
        "paths": {
            "output_directory": "qrcodes",
            "config_file": "micro_qr_config.json"
        },
        
        # 界面设置
        "ui": {
            "language": "zh_CN",
            "theme": "clam",
            "font_family": "Segoe UI",
            "font_size": 12
        }
    }
    
    def __init__(self, config_file: str = "micro_qr_config.json"):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"配置文件加载失败: {e}，使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 创建默认配置文件
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """
        保存配置文件
        
        Args:
            config: 要保存的配置，None 表示保存当前配置
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"配置文件保存失败: {e}")
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并默认配置和加载的配置
        
        Args:
            default: 默认配置
            loaded: 加载的配置
            
        Returns:
            合并后的配置
        """
        result = default.copy()
        
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]) -> None:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(result, loaded)
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def update_gui_settings(self, **kwargs) -> None:
        """
        更新 GUI 设置
        
        Args:
            **kwargs: GUI 设置参数
        """
        for key, value in kwargs.items():
            self.set(f"gui.{key}", value)
    
    def update_defaults(self, **kwargs) -> None:
        """
        更新默认参数
        
        Args:
            **kwargs: 默认参数
        """
        for key, value in kwargs.items():
            self.set(f"defaults.{key}", value)
    
    def get_gui_setting(self, key: str, default: Any = None) -> Any:
        """
        获取 GUI 设置
        
        Args:
            key: 设置键
            default: 默认值
            
        Returns:
            GUI 设置值
        """
        return self.get(f"gui.{key}", default)
    
    def get_default(self, key: str, default: Any = None) -> Any:
        """
        获取默认参数
        
        Args:
            key: 参数键
            default: 默认值
            
        Returns:
            默认参数值
        """
        return self.get(f"defaults.{key}", default)


# 全局配置实例
config = Config()
