import pymongo
import sys

def make_admin(email):
    try:
        client = pymongo.MongoClient('mongodb+srv://miladshehata513_db_user:MQcayQqoKL5VD6vY@cluster0.u4rzeua.mongodb.net/timeless?retryWrites=true&w=majority')
        db = client.get_database()
        result = db.users.update_one({'email': email}, {'$set': {'is_admin': True}})
        if result.matched_count > 0:
            print(f'Successfully made {email} an admin!')
        else:
            print(f'User with email {email} not found.')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    make_admin('test@example.com')
