import os
import re
import subprocess
from datetime import date

from django.core.management import call_command, CommandError

from frugal_protein import settings
from products.models import Brands, ProductInfo


class UpdateLiveDB:
    """
    This class inserts filtered products from local development database to the
    local live development database. Products are filtered by their protein 
    content (per 100g). This is to keep the number of database rows below the 
    10,000 limit for Heroku's psql free tier (500 rows reserved for django 
    backend)

    Attributes
        max_rows (str): maximum rows that can be inserted into db 
        protein_threshold (int/float): protein threshold for filtering
        live_db (str): db name listed under settings.DATABASES
    """

    max_rows = 9500
    protein_threshold = 10  # per 100g/ml
    live_db = 'live'
    
    def execute(self):
        self.reset_tables()

        # Get products greater than or equal to protein threshold
        candidate_products = ProductInfo.objects.filter(
            protein__gte=self.protein_threshold)
        products = candidate_products.filter(
            description__isnull=False,
            qty__isnull=False,
            protein__isnull=False
        )

        # Get brands found in filtered products
        brands = [p.brand for p in products]
        brands = set(brands)
        if None in brands:
            brands.remove(None)

        # Insert rows into live db
        total_rows = len(products) + len(brands)
        if total_rows <= self.max_rows:
            for brand in brands:
                brand.save(using=self.live_db)
            for product in products:
                product.save(using=self.live_db)
            print(f'{total_rows} rows inserted into local heroku db.',
                  f'{len(products)} products and {len(brands)} brands')
        else:
            msg = f'Too many rows! {total_rows}/{self.max_rows}'
            print(msg)
    
    def reset_tables(self):
        """ Reset (truncate) productinfo and brands table """
        call_command('flush', '--database=live', '--noinput')
        while len(ProductInfo.objects.using('live').all()) == 0 and \
              len(Brands.objects.using('live').all()) == 0:
              return

    def run_win_cmd(self, cmd):
        process =  subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        return process


class UpdateHeroku:
    """
    Two methods for updating psql db on Heroku:
        1. Heroku CLI provides a method 'pg:push' to push a local db to a Heroku
           db. Note that on Windows OS, this requires changing the PGUSER env
           variable from ROOT to a psql user.
        2. Manual push via pg_dump and pg_restore.
    """

    def execute(self):
        self.via_heroku_cli()
        # self.via_pg_restore()
    

    def run_win_cmd(self, cmd, **kwargs):
        process =  subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    **kwargs)
        return process


    def via_heroku_cli(self):
        """ Push local live db to remote heroku db via heroku's CLI """
        # Note: On Windows OS, pg:push requires changing PGUSER=ROOT to 
        # PGUSER={pguser} in the environment variables.
        # TODO validate successful push
        self.reset_heroku_db()
        local_db = settings.DATABASES['live']['NAME']
        heroku_db = os.getenv('HEROKU_DB_NAME')
        app = 'frugal-protein'
        cmd = f'heroku pg:push {local_db} {heroku_db} -a {app}'

        # PGUSER & PGPASSWORD variables set in virtual environment variables, 
        # thus must be collected and passed to subprocess
        env = os.environ
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        stdout, stderr = p.communicate()
        
        stdout = stdout.decode('utf-8')
        if 'Pushing complete' in stdout:
            print('local db successfully pushed to heroku db')
        else:
            stderr = stderr.decode('utf-8')
            raise CommandError(stderr)


    def via_pg_restore(self):
        self.reset_heroku_db()
        filename = f'{date.today()}.dump'
        path = os.path.join(settings.BASE_DIR, 'scrape', 'db_dumps', filename)
        local_db = settings.DATABASES['live']['NAME']
        self.dump_local(local_db, path)
        while not os.path.isfile(path):
            # Wait until local dump file has completed saving
            pass
        db_config = self.get_db_config()
        self.restore_heroku(db_config, path)
    

    def reset_heroku_db(self):
        cmd = 'heroku pg:reset DATABASE --confirm frugal-protein'
        p = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        print('heroku db resetted')


    def dump_local(self, db_name, filename):
        pguser = os.getenv('PGUSER')
        cmd = f'pg_dump --no-password --verbose -F c -Z 0 -U {pguser} -h localhost -p 5432 {db_name} > {filename}'
        env = os.environ
        p = self.run_win_cmd(cmd, env=env)
        p.communicate()
        print('pg_dump executed')


    def get_db_config(self):
        # pattern: postgres://<username>:<password>@<hostname>:<port>/<db_name>
        cmd = 'heroku config:get DATABASE_URL --app frugal-protein'
        process = self.run_win_cmd(cmd)
        res = [line for line in process.stdout]
        if len(res) == 1 and str(res[0]).startswith("b'postgres"):
            regex = "b'postgres:\/\/(\w+):(\w+)@(.+):(\d+)\/(\w+)"
            matches = re.findall(regex, str(res[0]))
            config = {
                'username': matches[0][0],
                'password': matches[0][1],
                'hostname': matches[0][2],
                'port': matches[0][3],
                'db_name': matches[0][4]
            }
            return config
        raise ValueError('Error retrieving db config')


    def restore_heroku(self, db_config, filename):
        user = db_config['username']
        pw = db_config['password']
        host = db_config['hostname']
        port = db_config['port']
        db = db_config['db_name']
        cmd = f'pg_restore --verbose --no-acl --no-owner -U {user} -h {host} -p {port} -d {db} < {filename}'
        
        env = os.environ
        os.environ['PGPASSWORD'] = pw
        p = self.run_win_cmd(cmd, env=env)
        p.communicate()
        print('pg_restore executed')
