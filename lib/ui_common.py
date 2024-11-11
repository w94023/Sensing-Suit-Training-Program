from PyQt5.QtGui import QColor

def format_color(color, format_type="rgba"):
    """Class color 변수의 getter method

    Args:
        vriable_name (object): class의 color 변수명
        format_type (str, optional): 
            option:"rgba"     > "rgba(255, 255, 255, 1)" 형식, PyQt에서 사용.
            option:"fraction" > (1, 1, 1, 1) 형식, matplotlib에서 사용.
            option:"QColor"   > QColor(255, 255, 255, 255) 형식.
            Defaults to "rgba".

    Returns:
        Not fixed: option에 따라 다른 형식 반환
    """
    
    r, g, b, a = color
    if format_type == "rgba":
        return f"rgba({r}, {g}, {b}, {a})"
    elif format_type == "fraction":
        return (r / 255, g / 255, b / 255, a)
    elif format_type == "QColor":
        return QColor(r, g, b, int(a*255))
    else:
        raise ValueError("Invalid format_type. Use 'rgba', 'fraction', or 'QColor'.")
        
class UiStyle:
    text_font = 'Arial'
    
    colors = {}
    # UI 컬러 스타일
    colors["background_color"]            = (0,   0,   0,   1  ) # app의 background color
    colors["line_color"]                  = (76,  76,  76,  1  ) # layout 간 구별을 위해 사용되는 line의 color
    colors["content_line_color"]          = (76,  76,  76,  0.5) # layout 내에 사용되는 옅은 line color
    colors["title_text_color"]            = (255, 255, 255, 1  ) # layout title에 사용되는 text color
    colors["title_bar_color"]             = (31,  91,  92,  1  ) # layout title bar에 사용되는 color
    colors["content_text_color"]          = (255, 255, 255, 0.5) # layout 내 content 표시에 사용되는 text color (title_text_color보다 연하게 설정)
    colors["content_hover_color"]         = (76,  76,  76,  0.5) # layout 내에서 선택 가능한 항목에 마우스 hover 시 사용되는 color
    colors["error_text_color"]            = (255, 0,   0,   0.6) # 특히 log에서, 에러가 발생했을 때 출력하는 text의 color (붉은 계열 색으로 설정)
    colors["minimize_button_hover_color"] = (100, 100, 100, 0.4) # layout title bar의 minimize button 마우스 hover 시 사용되는 color
    colors["close_button_hover_color"]    = (255, 0,   0,   0.4) # layout title bar의 close button 마우스 hover 시 사용되는 color
    # Plot 컬러 스타일
    colors["point_color_1"]               = (100, 100, 100, 0.5) # 회색
    colors["point_color_2"]               = (0,   120, 212, 0.5) # 파란색
    colors["point_color_3"]               = (252, 88,  126, 1  ) # 분홍색
    colors["point_color_4"]               = (234, 23,  12,  1  ) # 붉은색
    colors["point_color_5"]               = (31,  91,  92,  0.5) # 투명한 청록색
    colors["point_color_6"]               = (252, 88,  126, 0.5) # 투명한 분홍색
    colors["axis_color_1"]                = (255, 255, 255, 1  ) # 하얀색
    colors["axis_color_2"]                = (76,  76,  76,  1  ) # 연한 회색
    colors["axis_color_3"]                = (150, 150, 150, 1  ) # 짙은 회색
    colors["plot_color_1"]                = (86 , 233, 255, 1  ) # 청록 계열
    colors["plot_color_2"]                = (255, 183, 57,  1  ) # 오렌지 계열
    colors["plot_color_3"]                = (222, 65,  2,   1  ) # 빨강 계열
    colors["plot_color_1_transparent"]    = (86 , 233, 255, 0.5) # 청록 계열
    colors["plot_color_2_transparent"]    = (255, 183, 57,  0.5) # 오렌지 계열
    colors["plot_color_3_transparent"]    = (222, 65,  2,   0.5) # 빨강 계열
    # Plot 컬러맵
    plot_color_map = [
        format_color(colors["plot_color_1"], "fraction"),
        format_color(colors["plot_color_2"], "fraction"),
        format_color(colors["plot_color_3"], "fraction"),
    ]
    
    @classmethod
    def format_color(color, format_type="rgba"):
        return format_color(color, format_type)
    
    @classmethod
    def get_color(cls, color_label, format_type="rgba"):
        return format_color(cls.colors[color_label], format_type)
        
    @classmethod
    def get_plot_color(cls, index):
        return cls.plot_color_map[index % len(cls.plot_color_map)]