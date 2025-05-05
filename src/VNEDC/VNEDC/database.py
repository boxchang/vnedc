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


class scada_database:
    def select_sql(self, sql):
        with connections['SGADA'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['SGADA'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['SGADA'].cursor() as cur:
            cur.execute(sql)


class sap_database:
    def select_sql(self, sql):
        with connections['SAP'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['SAP'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['SAP'].cursor() as cur:
            cur.execute(sql)


class mes_database():
    plant = None

    def __init__(self, plant=None):
        if plant:
            self.plant = plant
        else:
            self.plant = "GD"

    def select_sql(self, sql):
        with connections[self.plant+"MES"].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections[self.plant+"MES"].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def select_sql_dict_param(self, sql, param):
        with connections[self.plant+"MES"].cursor() as cur:
            cur.execute(sql, param)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections[self.plant+"MES"].cursor() as cur:
            cur.execute(sql)


class vnedc_database:
    def select_sql(self, sql):
        with connections['VNEDC'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['VNEDC'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def select_sql_dict_param(self, sql, param):
        with connections['VNEDC'].cursor() as cur:
            cur.execute(sql, param)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['VNEDC'].cursor() as cur:
            cur.execute(sql)

    def execute_sql_custom(self, sql):
        with connections['VNEDC'].cursor() as cur:
            cur.execute(sql)
            return cur.rowcount

class gdmes_olap_database:
    def select_sql(self, sql):
        with connections['GD_OLAP'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['GD_OLAP'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def select_sql_dict_param(self, sql, param):
        with connections['GD_OLAP'].cursor() as cur:
            cur.execute(sql, param)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['GD_OLAP'].cursor() as cur:
            cur.execute(sql)

    def execute_sql_custom(self, sql):
        with connections['GD_OLAP'].cursor() as cur:
            cur.execute(sql)
            return cur.rowcount


class lkmes_olap_database:
    def select_sql(self, sql):
        with connections['LK_OLAP'].cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def select_sql_dict(self, sql):
        with connections['LK_OLAP'].cursor() as cur:
            cur.execute(sql)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def select_sql_dict_param(self, sql, param):
        with connections['LK_OLAP'].cursor() as cur:
            cur.execute(sql, param)
            desc = cur.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))
                    for row in cur.fetchall()]
            return data

    def execute_sql(self, sql):
        with connections['LK_OLAP'].cursor() as cur:
            cur.execute(sql)

    def execute_sql_custom(self, sql):
        with connections['LK_OLAP'].cursor() as cur:
            cur.execute(sql)
            return cur.rowcount