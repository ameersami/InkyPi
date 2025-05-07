from flask import Blueprint, request, jsonify, current_app, render_template
from utils.time_utils import calculate_seconds
import json
from pathlib import Path
import os
import logging
from utils.app_utils import resolve_path

logger = logging.getLogger(__name__)
display_bp = Blueprint("display", __name__)

ALLOWED_FILE_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
FILE_SAVE_DIR = resolve_path(os.path.join("static", "images", "saved"))

def handle_request_files(request_files):
    file_location_map = {}
    for key, file in request.files.items():
        file_name = file.filename
        if '.' not in file_name or file_name.rsplit('.', 1)[1].lower() not in ALLOWED_FILE_EXTENSIONS:
            continue
        file_name = os.path.basename(file_name)
        file_path = os.path.join(FILE_SAVE_DIR, file_name)
        file.save(file_path)
        file_location_map[key] = file_path
    return file_location_map

@display_bp.route('/get_all_images', methods=['GET'])
def handle_get_all_images():
    try:
      all_images = os.listdir(FILE_SAVE_DIR)
      return all_images
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@display_bp.route('/delete_image', methods=['DELETE'])
def handle_delete_image():
    try:
      file_name_to_delete = request.json
      file_path = os.path.join(Path(resolve_path("static")), "images", "saved", file_name_to_delete["fileName"])
      if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({ "message": "success" }), 200
      else:
        print("The file does not exist")
        return jsonify({ "message": "success" }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@display_bp.route('/update_now', methods=['POST'])
def update_now():
    device_config = current_app.config['DEVICE_CONFIG']
    refresh_task = current_app.config['REFRESH_TASK']

    try:
        plugin_settings = request.form.to_dict()  # Get all form data
        plugin_settings.update(handle_request_files(request.files))

        refresh_task.manual_update(plugin_settings)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Display updated"}), 200


@display_bp.route('/schedule_plugin', methods=['POST'])
def schedule_plugin():
    device_config = current_app.config['DEVICE_CONFIG']
    refresh_task = current_app.config['REFRESH_TASK']

    try:
        form_data = request.form.to_dict()
        refresh_settings = json.loads(form_data.pop("refresh_settings"))
        if not refresh_settings.get('interval') or not refresh_settings["interval"].isnumeric():
            raise RuntimeError("Invalid refresh interval.")
        if not refresh_settings.get('unit') or refresh_settings["unit"] not in ["minute", "hour", "day"]:
            raise RuntimeError("Invalid refresh unit.")

        plugin_settings = form_data
        plugin_settings.update(handle_request_files(request.files))

        refresh_interval_seconds = calculate_seconds(int(refresh_settings.get("interval")), refresh_settings.get("unit"))
        device_config.update_value("refresh_settings", {
            "interval": refresh_interval_seconds,
            "plugin_settings": plugin_settings
        })
        refresh_task.update_refresh_settings()
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    return jsonify({"success": True, "message": "Scheduled refresh configured."})
    