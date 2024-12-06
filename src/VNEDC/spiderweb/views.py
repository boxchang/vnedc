from django.shortcuts import render
from spiderweb.models import Device_Type, Monitor_Device_List, Monitor_Device_Log
from VNEDC.database import vnedc_database

def spiderweb(request):
    device_types = Device_Type.objects.all()
    monitor_list = [device.type_name for device in device_types if device.type_name != 'WECOM']
    monitor_mode = []
    monitor_name = []
    monitor_msg = []
    db = vnedc_database()
    for name in monitor_list:
        filtered_result = []
        # result = Monitor_Device_List.objects.filter(
        #     enable='Y',
        #     device_type__type_name=name,
        # ).select_related('device_type').order_by('device_type__id', 'device_group', 'device_name')
        sql = f"""
        select dt.id, dt.type_name, dl.status_id, dl.device_name, dlg.comment, s.ref_url,
        max(case when dl.status_id != 'S01' and enable = 'Y' and dlg.recover_msg is NULL and dl.device_type_id = dt.id then dlg.update_at end) as update_at
        from [VNEDC].[dbo].[spiderweb_device_type] dt
        join  [VNEDC].[dbo].[spiderweb_monitor_device_list] dl on dl.device_type_id = dt.id
        join [VNEDC].[dbo].[spiderweb_monitor_device_log] dlg on dlg.func_name = dt.type_name
		join [VNEDC].[dbo].[spiderweb_monitor_status] s on dl.status_id = s.status_code
        where dl.status_id != 'S01' and enable = 'Y' and dlg.recover_msg is NULL and type_name = '{name}'
        group by dt.id, dt.type_name, dl.status_id, dl.device_name, dlg.comment,s.ref_url
        """
        result = db.select_sql_dict(sql)
        filtered_result = [fresult for fresult in result if 'E' in fresult['status_id']]
        monitor_mode.append(len(set([str(item['device_name']) for item in filtered_result])))

        if str(name) == 'COUNTING DEVICE' or str(name) == 'AOI DEVICE':
            # monitor_name.append(','.join(sorted(list(set([f"{str(item.device_group).split('_')[-2][:-1]}{str(item.device_group).split('_')[-1][1:]}" for item in filtered_result])))))
            if str(name) == 'COUNTING DEVICE':
                monitor_name.append(','.join(sorted(list(set([str(item) for item in filtered_result])))))
                monitor_msg.append([[item['device_name'], item['update_at'], item['comment'], item['ref_url']] for item in filtered_result])
            elif str(name) == 'AOI DEVICE':
                monitor_name.append(','.join(sorted(list(set([str(item) for item in filtered_result])))))
                monitor_msg.append([[item['device_name'], item['update_at'], item['comment'], item['ref_url']] for item in filtered_result])
        elif str(name) == 'PLC SCADA':
            monitor_name.append(','.join(sorted(list(set([str(item) for item in filtered_result])))))
            monitor_msg.append([[item['device_name'], item['update_at'], item['comment'], item['ref_url']] for item in filtered_result])
        elif str(name) == 'MES JOB':
            monitor_name.append(','.join(sorted(list(set([str(item) for item in filtered_result])))))
            monitor_msg.append([[item['device_name'], item['update_at'], item['comment'], item['ref_url']] for item in filtered_result])
        elif str(name) == 'KEY_DEVICE' or str(name) == 'SAPTicket':
            monitor_name.append(','.join(sorted(list(set([str(item) for item in filtered_result])))))
            monitor_msg.append([[item['device_name'], item['update_at'], item['comment'], item['ref_url']] for item in filtered_result])

    monitor_web = zip(monitor_list, monitor_mode, monitor_name, monitor_msg)
    job_frequencies = list(Device_Type.objects.values_list('job_frequency', flat=True))
    reload_time = (min(map(int, job_frequencies))*1000)/50
    last_update_time = str((Monitor_Device_List.objects.filter(enable='Y').order_by('-status_update_at').values('status_update_at').first())['status_update_at']).split('.')[0]

    return render(request, 'spiderweb/spiderweb.html', locals())
