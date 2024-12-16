import os
import sys
import django
import boto3
from datetime import datetime
from django.conf import settings
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ecommerce.settings')
django.setup()

def create_backup():
    """Crée une sauvegarde de la base de données PostgreSQL"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{timestamp}.sql'
    
    # Construire la commande pg_dump
    db_settings = settings.DATABASES['default']
    env = os.environ.copy()
    env['PGPASSWORD'] = db_settings['PASSWORD']
    
    command = f'pg_dump -h {db_settings["HOST"]} -U {db_settings["USER"]} -d {db_settings["NAME"]} -F c -f {backup_file}'
    
    try:
        # Exécuter la sauvegarde
        os.system(command)
        print(f'Sauvegarde créée : {backup_file}')
        
        # Si AWS S3 est configuré, uploader la sauvegarde
        if hasattr(settings, 'AWS_ACCESS_KEY_ID') and settings.AWS_ACCESS_KEY_ID:
            upload_to_s3(backup_file)
        
        return True
    except Exception as e:
        print(f'Erreur lors de la sauvegarde : {str(e)}')
        return False

def upload_to_s3(file_path):
    """Upload la sauvegarde vers AWS S3"""
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3_path = f'backups/{os.path.basename(file_path)}'
        
        s3.upload_file(file_path, bucket_name, s3_path)
        print(f'Sauvegarde uploadée vers S3 : {s3_path}')
        
        # Supprimer le fichier local après l'upload
        os.remove(file_path)
        print('Fichier local supprimé')
        
        return True
    except Exception as e:
        print(f'Erreur lors de l\'upload vers S3 : {str(e)}')
        return False

def cleanup_old_backups():
    """Nettoie les anciennes sauvegardes sur S3"""
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Lister tous les backups
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix='backups/'
        )
        
        if 'Contents' in response:
            # Trier par date
            backups = sorted(response['Contents'], key=lambda x: x['LastModified'])
            
            # Garder seulement les 5 derniers backups
            if len(backups) > 5:
                for backup in backups[:-5]:
                    s3.delete_object(
                        Bucket=bucket_name,
                        Key=backup['Key']
                    )
                    print(f'Ancienne sauvegarde supprimée : {backup["Key"]}')
        
        return True
    except Exception as e:
        print(f'Erreur lors du nettoyage des sauvegardes : {str(e)}')
        return False

if __name__ == '__main__':
    if create_backup():
        cleanup_old_backups()
