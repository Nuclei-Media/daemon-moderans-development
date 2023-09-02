from quota_models import UserQuota
import datetime


def increase_quota(user_id, db, increase_amount, files_being_commited):
    current_quota = get_current_quota(user_id, db)

    increasing_query = UserQuota(
        user_quota=current_quota.user_quota + increase_amount,
        last_update=datetime.datetime(),
        amount_of_files=current_quota.amount_of_files + files_being_commited,
        owner_id=user_id,
    )
    db.add(increasing_query)
    db.commit()


def decrease_quota(user, increase_amount):
    ...


def get_current_quota(user_id, db):
    query = db.query(UserQuota).filter(UserQuota.owner_id == user_id).all()
    return query
