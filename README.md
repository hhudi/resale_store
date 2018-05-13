基于python3

pip install -r requirments.txt
项目根目录下： ./shart.sh
项目根目录下： flask db migrate
flask db upgrade

如果出错，查看数据库，show tables;更改version_num 项为最新migrations/version/最新***.py
