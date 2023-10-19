# BookingSystem

 Postman collection: https://documenter.getpostman.com/view/27326963/2s93eZxqw1

## Note:
<p>
1. <code>pip install virtualenv</code><br>
2. <code>virtualenv <"env-name"></code><br>
3. active env <code>source ./<"env-name">/bin/active</code> (for the linux user)
</p>

### step: 1
setup your local postgres

### step: 2
run <code> python manage.py makemigrations</code><br>
run <code> python manage.py migrate</code>

### step: 3
run <code> python manage.py runserver</code><br>

open the <a href="http://127.0.0.1:8000/api">this url http://127.0.0.1:8000/api </a>