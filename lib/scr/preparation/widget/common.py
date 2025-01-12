from ..common import *
from ..refiner import *
from ..wireframe import *

def set_label_style(label, height):
    label.setMaximumHeight(height)
    label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    label.setStyleSheet(f"""
                            background-color: {UiStyle.get_color("background_color")};
                            color: {UiStyle.get_color("content_text_color")};
                            font-family: {UiStyle.text_font};
                            border: none;
                            """)
    
def set_text_field_style(text_field, height):
    text_field.setMaximumHeight(height)
    text_field.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    text_field.setStyleSheet(f"""
                                background-color: {PyQtAddon.get_color("background_color")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                font-family: {PyQtAddon.text_font};
                                border: 1px solid {PyQtAddon.get_color("content_line_color")};
                                """)
    
def set_custom_line_edit_style(custom_line_edit, height, default_text):
    custom_line_edit.setMaximumHeight(height)
    custom_line_edit.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    custom_line_edit.set_text_in_line_edit(default_text) # 기본값 설정

def set_button_style(button, height):
    button.setMaximumHeight(height)
    button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    button.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {PyQtAddon.get_color("point_color_1")};
                                color: {PyQtAddon.get_color("content_text_color")};
                                padding: 4px 8px;
                                border-radius: 0px;
                                border: none;
                            }}
                            QPushButton:hover {{
                                background-color: {PyQtAddon.get_color("point_color_5")};
                                border: none;
                            }}
                            """)