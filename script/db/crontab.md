# 备份分布
    10.90.34.38

    0 1 * * * python /home/renxf/app/fhh-doc/script/db/db_backup.py > /data/logs/fhh-backup/backup.log 2>&1
    0 3 * * * python /home/renxf/app/fhh-doc/script/db/db_restore.py fhh_test > /data/logs/fhh-backup/restore.log 2>&1