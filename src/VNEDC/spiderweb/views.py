from django.shortcuts import render
from spiderweb.models import Device_Type, Monitor_Device_List

def spiderweb(request):
    try:
        device_types = Device_Type.objects.all()
        monitor_list = [device.type_name for device in device_types if device.type_name != 'WECOM']
        print(monitor_list)
        monitor_mode = []
        monitor_name = []
        for name in monitor_list:
            filtered_result = []
            result = Monitor_Device_List.objects.filter(
                enable='Y',
                device_type__type_name=name,
            ).select_related('device_type').order_by('device_type__id', 'device_group', 'device_name')
            filtered_result = [fresult for fresult in result if 'E' in fresult.status_id]
            monitor_mode.append(len(filtered_result))

            if str(name) == 'COUNTING DEVICE' or str(name) == 'AOI DEVICE':
                monitor_name.append(','.join(sorted(list(set([f"{str(item.device_group).split('_')[-2][:-1]}{str(item.device_group).split('_')[-1][1:]}" for item in filtered_result])))))
            elif str(name) == 'PLC SCADA':
                monitor_name.append(','.join(sorted(list(set([f"{str(item.device_name).split('_')[-2][:-1]}{str(item.device_name).split('_')[-1][1:]}" for item in filtered_result])))))
            elif str(name) == 'MES JOB':
                monitor_name.append(','.join(sorted(list(set([f"{str(item.device_name).split('_')[0]}" for item in filtered_result])))))
            elif str(name) == 'KEY_DEVICE' or str(name) == 'SAPTicket':
                monitor_name.append(','.join(sorted(list(set([f"{str(item.device_name)}" for item in filtered_result])))))

        monitor_web = zip(monitor_list, monitor_mode, monitor_name)
        job_frequencies = list(Device_Type.objects.values_list('job_frequency', flat=True))
        reload_time = min(map(int, job_frequencies))*1000
        last_update_time = str((Monitor_Device_List.objects.filter(enable='Y').order_by('-status_update_at').values('status_update_at').first())['status_update_at']).split('.')[0]

    except:
        pass
    return render(request, 'spiderweb/spiderweb.html', locals())
