from integralstor_utils import scheduler_utils, common, logger
import logging


def main():

    lg = None
    try:
        lg, err = logger.get_script_logger(
            'Task processor', '/var/log/integralstor/scripts.log', level=logging.DEBUG)

        logger.log_or_print(
            'Task processor execution initiated.', lg, level='info')

        db_path, err = common.get_db_path()
        if err:
            raise Exception(err)
        ret, err = scheduler_utils.process_tasks()
        if err:
            raise Exception(err)
    except Exception, e:
        str = 'Error running the task processor : %s' % e
        logger.log_or_print(str, lg, level='critical')
        return -1
    else:
        str = 'Task processor execution complete.'
        logger.log_or_print(str, lg, level='info')
        return 0


if __name__ == "__main__":
    main()

# vim: tabstop=8 softtabstop=0 expandtab ai shiftwidth=4 smarttab
