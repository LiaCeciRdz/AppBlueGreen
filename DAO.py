import time
from botocore.exceptions import ClientError
import boto3
import time
import csv
import re
from flask_login import UserMixin

session = boto3.Session(aws_access_key_id='AKIAZBKYWXV4BQJD24P3', aws_secret_access_key='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')

params = {
    'region': 'us-east-1',
    'database': 'default',
    'bucket': 'compucloud-clientes-logs',
    'path': 'athena/output',
    'catalog': 'AwsDataCatalog'
}

class athena():

    def execute_custom_query(self, query, max_execution=800):
        # Ejecuto la consulta en athena y la almaceno en el bucket de S3.
        athena = session.client('athena', region_name=params["region"])
        execution = ''
        try:
            execution = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': params['database'],
                    'Catalog': params['catalog']
                },
                ResultConfiguration={
                    'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
                }
            )

        except ClientError as e:
            return "Incorrect syntax: {}".format(e)

        execution_id = execution['QueryExecutionId']

        # Verifico el estatus de la consulta y obtengo el nombre del archivo csv.
        state = 'RUNNING'
        filename = ''
        while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
            max_execution = max_execution - 1
            try:
                response = athena.get_query_execution(QueryExecutionId=execution_id)
            except ClientError as e:
                return "Error: {}".format(e)

            if 'QueryExecution' in response and 'Status' in response['QueryExecution'] and 'State' in \
                    response['QueryExecution']['Status']:
                state = response['QueryExecution']['Status']['State']
                if state == 'FAILED':
                    return False
                elif state == 'SUCCEEDED':
                    s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                    filename = re.findall('.*\/(.*)', s3_path)[0]
            time.sleep(1)

        # Leer datos de la consulta desde el archivo CSV almacenado en el bucket
        s3_client = session.resource('s3', region_name=params["region"])
        bucket = params['bucket']
        key = '{}/{}'.format(params['path'], filename)
        print(key)
        try:
            s3_obj = s3_client.Object(bucket, key.replace('+', ' '))
        except ClientError as e:
            return "Error: {}".format(e)
        data = s3_obj.get()['Body'].read()
        data_csv = csv.DictReader(data.decode('utf-8').split('\n'), delimiter=',')
        rows = [l for l in data_csv]
        # Limpiar bucket
        '''s3 = session.resource('s3', region_name=params["region"])
        try:
            my_bucket = s3.Bucket(params['bucket'])
        except ClientError as e:
            return "Error: {}".format(e)
        for item in my_bucket.objects.filter(Prefix=params['path']):
            item.delete()'''
        return rows

class Usuario(UserMixin):
    def __init__(self,Clave,Cuenta,Email,Empresa,Nombre):
          self.Clave = Clave
          self.Cuenta = Cuenta
          self.Email = Email
          self.Empresa = Empresa
          self.Nombre = Nombre

    def get_id(self):
        return self.Email

    def is_authenticated(self):
        return True

    def is_active(self):
        if self.estatus == 'Activo':
            return True
        else:
            return False

    #Validar
    '''def init_user(self, response, Clavee):
        self.Email = response["Email"]["S"]

        if "Clave" in response:
            self.Clave = response["Clave"]["S"]
            if self.Clave == Clavee:
                print('Contraseña correcta')
                print(self)
                return self
            else:
                print('Contraseña incorrecta')
                return None'''
