#!/bin/bash

MANAGE_PY_PATH="/code/manage.py"

create_superuser() {
    echo "Creating superuser..."
    python $MANAGE_PY_PATH createsuperuser --noinput --username admin --email admin@example.com

    if [ $? -eq 0 ]; then
        echo "Superuser 'admin' created successfully with password 'admin'."
    else
        echo "Error creating superuser."
    fi
}

create_superuser