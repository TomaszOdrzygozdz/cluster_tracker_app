import csv
from subprocess import check_output, PIPE

def check_cluster(user, host):
    rich_squeue = 'source .bash_scripts/squeue.sh'
    output = check_output(f'ssh {user}@{host} "{rich_squeue}"', shell=True, stderr=PIPE)
    return process_output(output)

def process_output(output):
    out_lines = output.decode("utf-8").splitlines()
    jobs_list = []
    job_fields = out_lines.pop(0).split('|')
    for line in out_lines:
        jobs_list.append(line.split('|'))
    return (job_fields, jobs_list)

def load_database(database_file):
    with open(database_file, newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def squeue_to_html(caption, header, content):
    squque_html = '<style type="text/css">' \
                '.tg  {border-collapse:collapse;border-color:#ccc;border-spacing:0;}' \
                '.tg td{background-color:#fff;border-color:#ccc;border-style:solid;border-width:1px;color:#333;' \
                '  font-family:Arial, sans-serif;font-size:14px;overflow:hidden;padding:10px 5px;word-break:normal;}' \
                '.tg th{background-color:#f0f0f0;border-color:#ccc;border-style:solid;border-width:1px;color:#333;' \
                '  font-family:Arial, sans-serif;font-size:14px;font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}' \
                '.tg .tg-ulak{background-color:#e2e0e0;border-color:inherit;text-align:left;vertical-align:top}' \
                '.tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}' \
                '</style>'
    squque_html += '<table class="tg">' \
                 f'<tr> <td colspan=100%><center><b>{caption}</b> </center> </td> </tr>' \
                 '<tr>'

    for field in header:
        squque_html += f'<td class="tg-ulak"><b>{field}</b></th>'
    squque_html += '<td class="tg-0pky">' + add_button_to_html('scancel', 'all', 'scancel all', True) + '</td></tr>'
    for entry in content:
        job_id = entry[0]
        squque_html += '<tr>'
        for value in entry:
            squque_html += f'<td class="tg-0pky">{value}</td>'
        squque_html += '<td class="tg-0pky">' + add_button_to_html('scancel', f'{job_id}', 'scancel', True) + '</td>'
        squque_html += '</tr>'
    return squque_html

def database_to_html(caption, content):
    database_html = '<style type="text/css">' \
                '.tg  {border-collapse:collapse;border-color:#ccc;border-spacing:0;}' \
                '.tg td{background-color:#fff;border-color:#ccc;border-style:solid;border-width:1px;color:#333;' \
                '  font-family:Arial, sans-serif;font-size:14px;overflow:hidden;padding:10px 5px;word-break:normal;}' \
                '.tg th{background-color:#f0f0f0;border-color:#ccc;border-style:solid;border-width:1px;color:#333;' \
                '  font-family:Arial, sans-serif;font-size:14px;font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}' \
                '.tg .tg-ulak{background-color:#e2e0e0;border-color:inherit;text-align:left;vertical-align:top}' \
                '.tg .tg-wrap{background-color:#e2e0e0;border-color:inherit;text-align:left;vertical-align:top;width:10%}' \
                '.tg .tg-0pky{border-color:inherit;text-align:left;vertical-align:top}' \
                '</style>'
    database_html += '<table class="tg">' \
                 f'<tr> <td colspan=100%><center><b>{caption}</b> </center> </td> </tr>' \
                 '<tr>'

    header = content.pop(0)
    scratch_dir_index = header.index('Scratch dir')
    log_file_index = header.index('Log file')
    for field in header:
        if field == 'Scratch dir' or field == 'Log file':
            database_html += f'<td class="tg-wrap"><b>{field}</b></th>'
        else:
            database_html += f'<td class="tg-ulak"><b>{field}</b></th>'
    # database_html += '<td class="tg-0pky">' + add_button_to_html('open log', 'all', 'scancel all', True) + '</td></tr>'

    for num, entry in enumerate(content):
        database_html += '<tr>'
        for value in entry:
            database_html += f'<td class="tg-0pky">{value}</td>'
        database_html += '<td class="tg-0pky"><center>' + add_button_to_html('open_log', f'{entry[log_file_index]}', 'open log', True) + '</center></td>'
        database_html += '<td class="tg-0pky"><center>' + add_button_to_html('open_dir_eagle', f'{entry[scratch_dir_index]}', 'dir eagle', True) + '</center></td>'
        database_html += '<td class="tg-0pky"><center>' + add_button_to_html('open_dir_prom',  f'{entry[scratch_dir_index]}', 'dir prometheus', True) + '</center></td>'
        database_html += '<td class="tg-0pky"><center>' + add_button_to_html('del_entry',  f'{num}', 'del', True) + '</center></td>'
        database_html += '</tr>'
    return database_html

def add_button_to_html(function, value, caption, wrap_in_form=False):
    code = f'<button class="btn btn-danger" type="submit" name="{function}" value="{value}"> {caption} </button>'
    if wrap_in_form:
        code = '<form action = "" method = "POST" >' + code + '</form>'
    return code

def scancel(job_id, user, host):
    if job_id != 'all':
        check_output(f'ssh {user}@{host} "scancel {job_id}"', shell=True, stderr=PIPE)
    elif job_id == 'all':
        check_output(f'ssh {user}@{host} "scancel -u {user}"', shell=True, stderr=PIPE)
    else:
        raise ValueError('Uknown scancel mode.')

def open_log(user_info, file_path):
    prom_user = user_info['prometheus']['user']
    prom_host = user_info['prometheus']['host']
    eagle_user = user_info['eagle']['user']
    eagle_host = user_info['eagle']['host']
    editor = user_info['editor']
    out_file = user_info['out_file']

    command_prometheus = f'scp {prom_user}@{prom_host}:{file_path} {out_file}'
    command_eagle = f'scp {eagle_user}@{eagle_host}:{file_path} {out_file}'
    command_scp = command_prometheus + ' || ' + command_eagle
    check_output(command_scp, shell=True, stderr=PIPE)
    check_output(f'{editor} {out_file}', shell=True, stderr=PIPE)

def open_dir_eagle(user_info, path):

    eagle_user = user_info['eagle']['user']
    eagle_host = user_info['eagle']['host']
    file_browser = user_info['file_browser']

    command_eagle = f'{file_browser} sftp://{eagle_user}@{eagle_host}{path}'
    check_output(command_eagle, shell=True, stderr=PIPE)


def open_dir_prom(user_info, path):
    prom_user = user_info['prometheus']['user']
    prom_host = user_info['prometheus']['host']
    file_browser = user_info['file_browser']
    command_prometheus = f'{file_browser} sftp://{prom_user}@{prom_host}{path}'
    check_output(command_prometheus, shell=True, stderr=PIPE)

def del_entry(line_num, database_file):
    line_num = int(line_num)
    with open(database_file) as database:
        lines = database.readlines()
        lines = lines[:line_num+1] + lines[line_num+2:]
        with open(database_file, "w") as f:
            f.writelines(lines)