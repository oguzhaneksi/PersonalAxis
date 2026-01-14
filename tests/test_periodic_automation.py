import os
import xml.etree.ElementTree as ET
import pytest

def test_daily_plist_structure():
    plist_path = "automation/launchd/com.personalaxis.daily.plist"
    assert os.path.exists(plist_path)
    
    tree = ET.parse(plist_path)
    root = tree.getroot()
    
    # Check basic structure
    dict_elem = root.find("dict")
    assert dict_elem is not None
    
    # Convert dict to Python dict for easier checking
    keys = [k.text for k in dict_elem.findall("key")]
    assert "Label" in keys
    assert "ProgramArguments" in keys
    assert "StartCalendarInterval" in keys

    # Check for placeholder in StartCalendarInterval
    for i, child in enumerate(dict_elem):
        if child.tag == "key" and child.text == "StartCalendarInterval":
            interval_dict = dict_elem[i+1]
            for j, k in enumerate(interval_dict):
                if k.tag == "key" and k.text == "Hour":
                    assert interval_dict[j+1].text == "__DAILY_HOUR__"

def test_weekly_plist_schedule():
    plist_path = "automation/launchd/com.personalaxis.weekly.plist"
    tree = ET.parse(plist_path)
    root = tree.getroot()
    
    # Find StartCalendarInterval dict
    dict_elem = root.find("dict")
    found_interval = False
    
    # This is a bit manual because of how plist is structured in XML
    for i, child in enumerate(dict_elem):
        if child.tag == "key" and child.text == "StartCalendarInterval":
            interval_dict = dict_elem[i+1]
            interval_keys = [k.text for k in interval_dict.findall("key")]
            assert "Weekday" in interval_keys
            # Check that placeholders are present in the template plists
            weekday_val = None
            for j, k in enumerate(interval_dict):
                if k.tag == "key" and k.text == "Weekday":
                    weekday_val = interval_dict[j+1].text
            assert weekday_val == "__WEEKLY_DAY__"
            found_interval = True
            break
    assert found_interval

def test_install_script_logic():
    install_script = "automation/install.sh"
    assert os.path.exists(install_script)
    
    with open(install_script, 'r') as f:
        content = f.read()
    
    # Verify key logic exists
    assert "PROJECT_DIR=" in content
    assert "VENV_PYTHON=" in content
    assert "DAILY_HOUR=" in content
    assert "WEEKLY_DAY=" in content
    assert "MONTHLY_DAY=" in content
    assert "sed -i ''" in content or "sed -i" in content
    assert "launchctl load" in content

def test_monthly_plist_schedule():
    plist_path = "automation/launchd/com.personalaxis.monthly.plist"
    tree = ET.parse(plist_path)
    root = tree.getroot()
    
    dict_elem = root.find("dict")
    found_interval = False
    
    for i, child in enumerate(dict_elem):
        if child.tag == "key" and child.text == "StartCalendarInterval":
            interval_dict = dict_elem[i+1]
            interval_keys = [k.text for k in interval_dict.findall("key")]
            assert "Day" in interval_keys
            # Check that placeholders are present in the template plists
            day_val = None
            for j, k in enumerate(interval_dict):
                if k.tag == "key" and k.text == "Day":
                    day_val = interval_dict[j+1].text
            assert day_val == "__MONTHLY_DAY__"
            found_interval = True
            break
    assert found_interval
