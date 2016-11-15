from integralstor_common import scheduler_utils, common, logger
import logging


def main():

  lg = None
  try :
    lg, err = logger.get_script_logger('Scheduler', '/var/log/integralstor/scripts.log', level = logging.DEBUG)

    logger.log_or_print('Scheduler execution initiated.', lg, level='info')

    db_path,err = common.get_db_path()
    if err:
      raise Exception(err)
    ret, err = scheduler_utils.execute_scheduler(db_path)
    if err:
      raise Exception(err)
  except Exception, e:
    str = 'Error running the scheduler : %s'%e
    logger.log_or_print(str, lg, level='critical')
    return -1
  else:
    str = 'Scheduler execution complete.'
    logger.log_or_print(str, lg, level='info')
    return 0


if __name__ == "__main__":
  main()
