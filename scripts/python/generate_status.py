#!/usr/bin/python

from integralstor_common import lock, common, manifest_status, logger
import json, os, shutil, datetime, sys, re, logging
import pprint

  
def gen_status(path):
  try :
    lck, err = lock.get_lock('generate_status')
    if err:
      raise Exception(err)
    if not lck:
      raise Exception('Generate Status : Could not acquire lock.')
    fullmanifestpath = os.path.normpath("%s/master.manifest"%path)
    ret, err = manifest_status.generate_status_info(fullmanifestpath)
    if not ret :
      if err:
        raise Exception(err)
      else:
        raise Exception('No status info obtained')
    fullpath = os.path.normpath("%s/master.status"%path)
    fulltmppath = "/tmp/master.status.tmp"
    #Generate into a tmp file
    with open(fulltmppath, 'w') as fd:
      json.dump(ret, fd, indent=2)
    #Now move the tmp to the actual manifest file name
    shutil.move(fulltmppath, fullpath)
  except Exception, e:
    lock.release_lock('generate_status')
    return -1,  'Error generating status : %s'%str(e)
  else:
    lock.release_lock('generate_status')
    return 0, None

import atexit
atexit.register(lock.release_lock, 'generate_status')

def main():

  lg = None
  try :
    lg, err = logger.get_script_logger('Generate status', '/var/log/integralstor/scripts.log', level = logging.DEBUG)

    logger.log_or_print('Generate status initiated.', lg, level='info')

    platform, err = common.get_platform()
    if err:
      raise Exception(err)

    if platform == 'gridcell':
      from integralstor_gridcell import grid_ops
      active, err = grid_ops.is_active_admin_gridcell()
      if err:
        raise Exception(err)
      if not active:
        logger.log_or_print('Not active admin GRIDCell so exiting.', lg, level='info')
        sys.exit(0)
    num_args = len(sys.argv)
    if num_args > 1:
      path = sys.argv[1]
    else:
      path, err = common.get_system_status_path()
      if err:
        raise Exception(err)
      if not path:
        path = '/tmp'
    logger.log_or_print("Generating the status in %s"%path, lg, level='info')
    rc, err = gen_status(path)
    if err:
      raise Exception(err)
    #print rc
  except Exception, e:
    str = "Error generating status file : %s"%e
    logger.log_or_print(str, lg, level='critical')
    sys.exit(-1)
  else:
    logger.log_or_print('Generate status completed successfully.', lg, level='info')
    sys.exit(0)


if __name__ == "__main__":
  main()
