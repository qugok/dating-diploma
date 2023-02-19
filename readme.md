git clone git@github.com:qugok/dating-diploma.git
sudo python -m pip install grpcio
python -m pip install grpcio-tools

make
cd python && python gui_client.py
