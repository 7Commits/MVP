import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from views import ui_utils, style_utils, component_utils


def test_ui_utils_re_exports_functions():
    assert ui_utils.add_global_styles is style_utils.add_global_styles
    assert ui_utils.add_page_header is style_utils.add_page_header
    assert ui_utils.add_section_title is style_utils.add_section_title
    assert ui_utils.create_card is component_utils.create_card
    assert ui_utils.create_metrics_container is component_utils.create_metrics_container
    expected_all = {
        'add_global_styles',
        'add_page_header',
        'add_section_title',
        'create_card',
        'create_metrics_container',
    }
    assert set(ui_utils.__all__) == expected_all
