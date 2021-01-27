import sys

sys.path.extend(['/home/tomek/Research/cluster_tracker',
                 '/home/tomek/anaconda3/envs/cluster_tracker/lib/python36.zip',
                 '/home/tomek/anaconda3/envs/cluster_tracker/lib/python3.6',
                 '/home/tomek/anaconda3/envs/cluster_tracker/lib/python3.6/lib-dynload',
                 '/home/tomek/anaconda3/envs/cluster_tracker/lib/python3.6/site-packages'])

import webbrowser
import yaml
from werkzeug.utils import redirect

from flask import Flask, request, url_for
from backend import squeue_to_html, add_button_to_html, check_cluster, scancel, load_database, database_to_html, \
    open_log, open_dir_eagle, open_dir_prom, del_entry

app = Flask(__name__)
credentials = {}
user_info = {}
content = {'squeue': None, 'database' : None}

def handle_website_request(name, value):
    global credentials
    global user_info
    if name == 'squeue':
        credentials = user_info[value]

        content['squeue'] = check_cluster(credentials['user'], credentials['host'])
        content['cluster_name'] = value

    if name == 'scancel':
        scancel(value, credentials['user'], credentials['host'])
        content['squeue'] = check_cluster(credentials['user'], credentials['host'])
        return redirect(url_for('home'))

    if name == 'open_log':
        open_log(user_info, value)

    if name == 'open_dir_eagle':
        open_dir_eagle(user_info, value)

    if name == 'open_dir_prom':
        open_dir_prom(user_info, value)

    if name == 'del_entry':
        del_entry(value, user_info['database_file'])


@app.route("/", methods=['GET', 'POST'])
def home():
    global user_info
    if user_info == {}:
        with open('config.yaml', 'r') as stream:
            user_info = yaml.safe_load(stream)

    if request.method == 'POST':
        request_data = request.form.to_dict()
        handle_website_request(*list(request_data.items())[0])
    return prepare_website()


def prepare_website():
    html_code = '<meta http-equiv="refresh" content="30" /><body>'
    # job_fields, job_list = check_eagle()
    html_code += '<form action = "" method = "POST">'
    html_code += add_button_to_html('squeue', 'eagle', 'Load Eagle jobs')
    html_code += add_button_to_html('squeue', 'prometheus', 'Load Prometheus jobs')
    html_code += '</form>'
    html_code += '<hr>'

    if content['squeue'] is not None:
        html_code += squeue_to_html(content['cluster_name'], *content['squeue'])

    content['database'] = load_database(user_info['database_file'])
    html_code += database_to_html('Deployed experiments', content['database'])
    html_code += '</body>'
    return html_code

if __name__ == "__main__":
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()