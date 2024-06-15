from django.db import connections


class database:
    def execute_sql(self, sql):
        with connections['default'].cursor() as cur:
            cur.execute(sql)

    def select_sql(self, sql):
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['default'].cursor() as cur:
            cur.execute(sql)

            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data


class bpm_database:
    def select_sql(self, sql):
        with connections['BPM'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['BPM'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['BPM'].cursor() as cur:
            cur.execute(sql)


class dc_database:
    def select_sql(self, sql):
        with connections['DC'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['DC'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['DC'].cursor() as cur:
            cur.execute(sql)

