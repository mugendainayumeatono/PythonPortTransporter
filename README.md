# PythonPotrTransporter

this is a reomot port transporter<br>
it is very similar "ssh -L"<br>
all the transport data aer encrypt by aes-cfb256<br>
and the encrypt keys are pre-confirmed between server and client<br>
so it do not use RSA to exchange the keys<br>
and do not has any heartbeat packet<br>

I make this new wheel becaus openssh stream have obviously characteristic<br>
some one can discover you aer useing ssh as a proxy but not useing ssh as a linux shell<br>
they will break the connection or limite link speed<br>

# notice
only python3 support<br>

must install pycrypto 2.6.1 first<br>
you can download here <br>
<https://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.6.1.tar.gz>
and do<br>
>tar -zxvf pycrypto-2.6.1.tar.gz  
>cd pycrypto-2.6.1  
>make  
>make install  

# usage
normal transport without encrypt<br>
python main.py -n --ip=remoteServerIP --rport=remoteServicePort --lport=transportToThisPort<br>

encrypt transport server peer<br>
python main.py -s --ip=127.0.0.1 --rport=ServicePort --lport=clientConnectToThisPort --key=password<br>

encrypt transport client peer<br>
python main.py -c --ip=serverIP --rport=Server-lport --lport=transportServicePortToHere --key=password<br>

#changelog
v0.1 release<br>
