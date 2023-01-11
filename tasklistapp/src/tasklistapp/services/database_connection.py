import mysql.connector

sql_query_template = {}

sql_query_template["get_dcr_role"] = f"SELECT Role FROM DCRUsers WHERE Email = %(email)s"
sql_query_template["insert_new_instance"] = "INSERT INTO instances VALUES (%s, %s, %s)"
sql_query_template["delete_instance"] = "DELETE FROM instances WHERE SimsID = %s"
sql_query_template["print_instances_table"] = "SELECT * FROM instances"

def db_connect():
    cnx = mysql.connector.connect(user="group2",
                                password="db_password",
                                host="tasklistdb.mysql.database.azure.com",
                                port=3306,
                                database="tasklistdatabase",
                                ssl_ca="../resources/DigiCertGlobalRootCA.crt.pem",
                                ssl_disabled=False)

    print(f'[i] cnx is connected: {cnx.is_connected()}')
    return cnx

def execute_query(sql_query_name, data_dict):
    try:
        res = None
        cnx = db_connect()
        cursor = cnx.cursor(buffered=True)
        cursor.execute(sql_query_template[sql_query_name], data_dict)
        if sql_query_template[sql_query_name].startswith("SELECT"):
            res = cursor
        if sql_query_template[sql_query_name].startswith("INSERT") or sql_query_template[sql_query_name].startswith("DELETE"):
            cnx.commit()
        cursor.close()
        cnx.close()
        return res
    except Exception as ex:
        print(f'[x] error! {ex}')
        return None