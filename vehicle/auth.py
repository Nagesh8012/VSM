def is_customer(user):
    return user.groups.filter(name="CUSTOMER").exists()


def is_staff(user):
    return user.groups.filter(name="STAFF").exists()

