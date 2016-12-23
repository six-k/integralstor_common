#!/usr/bin/python
import sys, time

from integralstor_common import common, alerts, lock, command, zfs

import atexit
atexit.register(lock.release_lock, 'poll_for_alerts')
atexit.register(lock.release_lock, 'gluster_commands')

def main():
  try :
    platform, err = common.get_platform()
    if err:
      raise Exception(err)


    lck, err = lock.get_lock('poll_for_alerts')
    if err:
      raise Exception(err)
    if not lck:
      raise Exception('Could not acquire lock. Exiting.')


    if platform == 'gridcell':
      from integralstor_gridcell import system_info
      gluster_lck, err = lock.get_lock('gluster_commands')
    else:
      from integralstor_unicell import system_info

    si, err = system_info.load_system_config()
    if platform == 'gridcell':
      lock.release_lock('gluster_commands')
    if err:
      raise Exception(err)
    if not si:
      raise Exception('Could not load system information')

    alert_list = []
  
    for node_name, node in si.items():
      if 'errors' in node and node['errors']:
        if platform == 'gridcell':
          msg = 'GRIDCell : %s. '%node_name
        else:
          msg = ''
        msg += '. '.join(node['errors'])
      
        alert_list.append(msg)

    hw_platform, err = common.get_hardware_platform()
    if hw_platform:
      if hw_platform == 'dell':
        from integralstor_common.platforms import dell
        alerts_dict, err = dell.get_alert_logs()
        if alerts_dict:
          current_time = int(time.time())
          for time_stamp, alerts_list in alerts_dict.items():
            for alert_dict in alerts_list:
              if alert_dict['Severity'] == 'Critical':
                if (current_time - time_stamp) < (60*60):
                  alert_list.append(alert_dict['description'])
                  #print time_stamp, alert_dict

    #print "======================"
    #print alert_list
    #print "======================"
    if alert_list:
      alerts.raise_alert(alert_list)

    lock.release_lock('poll_for_alerts')
  except Exception, e:
    print "Error generating alerts : %s ! Exiting."%str(e)
    sys.exit(-1)
  else:
    sys.exit(0)

if __name__ == "__main__":
  main()


'''
def node_up(node):
    # Check node status
    if "node_status" in node:
      if node["node_status"] != 0:
        if node["node_status"] < 0:
          return False 
    return True
def check_disk_status(node, node_name, platform):

  alert_list = []
  try: 
    common_python_scripts_path, err = common.get_common_python_scripts_path()
    if err:
      raise Exception(err)
    shell_scripts_path, err = common.get_shell_scripts_path()
    if err:
      raise Exception(err)
    disk_signalling_list = []
    s = ""
    if "disks" in node:
      disks = node["disks"]
      for sn, disk in disks.items():
        if "status" in disk and disk['status'] != None and disk["status"] not in ['PASSED', 'OK']:
          disk_signalling_list.append({'scsi_info': disk['scsi_info'], 'action':'ON'})
          if platform == 'unicell':
            alert_list.append("Disk with serial number %s has problems."%(sn))
          else:
            alert_list.append("GRIDCell : %s. Disk with serial number %s has problems."%(node_name, sn))
        else:
          disk_signalling_list.append({'scsi_info': disk['scsi_info'], 'action':'OFF'})
    #drive_signalling.signal_drives(disk_signalling_list)

  except Exception, e:
    return None, 'Error checking disk status : %s'%str(e)
  else:
    return alert_list, None


def check_ipmi_status(node, node_name, platform):

  alert_list = []
  try:
    if "ipmi_status" in node:
      status_list = node["ipmi_status"]
      for status_item in status_list:
        if status_item["status"] not in ['ok', 'nr']:
          if platform == 'unicell':
            m = "The %s of the %s is reporting errors" %(status_item["parameter_name"], status_item["component_name"])
          else:
            m = "GRIDCell : %s. The %s of the %s is reporting errors" %(node_name, status_item["parameter_name"], status_item["component_name"])
          if "reading" in status_item:
            m += " with a reading of %s."%status_item["reading"]
          alert_list.append(m)
  except Exception, e:
    return None, 'Error checking ipmi status : %s'%str(e)
  else:
    return alert_list, None

def check_interface_status(node, node_name, platform):

  alert_list = []
  try:
    #print node.keys()
    if "interfaces" in node:
      interfaces = node["interfaces"]
      for if_name, interface in interfaces.items():
        if 'lo' in if_name:
          continue
        #print if_name, interface
        #if 'slave_to' in interface or ('addresses' in interface and 'AF_INET' in interface['addresses']):
        if "status" in interface and interface["status"] != 'up':
          if platform == 'unicell':
            alert_list.append("The network interface %s has problems."%(if_name))
          else:
            alert_list.append("GRIDCell : %s. The network interface %s has problems."%(node_name, if_name))
  except Exception, e:
    return None, 'Error checking interface status : %s'%str(e)
  else:
    return alert_list, None

def check_pool_status(node, node_name, platform):

  alert_list = []
  try:
    if "pools" in node:
      pools = node["pools"]
      component_status_dict, err = zfs.get_all_components_status(pools)
      if err:
        raise Exception(err)
      if component_status_dict:
        for pool_name, component_status_list in component_status_dict.items():
          msg = None
          for component in component_status_list:
            if 'status' in component and 'state' in component['status'] and component['status']['state'] != 'ONLINE':
              if not msg:
                if platform == 'unicell':
                  msg = "The ZFS pool '%s' has the following issue(s) : "%pool_name
                else:
                  msg = "GRIDCell : %s. The ZFS pool '%s' has the following issue(s) : "%(node_name, pool_name)
              msg += "The component %s of type '%s' has a state of '%s'. "%(component['name'], component['type'], component['status']['state'])
          if msg:
            alert_list.append(msg)
  except Exception, e:
    return None, 'Error checking pool status : %s'%str(e)
  else:
    return alert_list, None


def check_load_average(node, node_name, platform):

  alert_list = []
  try:
    if "load_avg" in node:
      if node["load_avg"]["5_min"] > node["load_avg"]["cpu_cores"]:
        if platform == 'unicell':
          alert_list.append("The 5 minute load average has been high with a value of %.2f."%(node["load_avg"]["5_min"]))
        else:
          alert_list.append("GRIDCell : %s. The 5 minute load average has been high with a value of %.2f."%(node_name, node["load_avg"]["5_min"]))
      if node["load_avg"]["15_min"] > node["load_avg"]["cpu_cores"]:
        if platform == 'unicell':
          alert_list.append("The 15 minute load average on has been high with a value of %.2f."%(node["load_avg"]["15_min"]))
        else:
          alert_list.append("GRIDCell : %s. The 15 minute load average on has been high with a value of %.2f."%(node_name, node["load_avg"]["15_min"]))
  except Exception, e:
    return None, 'Error checking pool status : %s'%str(e)
  else:
    return alert_list, None

'''
