#!/usr/bin/env python3

import socket
import time
import gmpy2
import functools

def det(i,j,k,l,X):
	return (X[i]*X[k] - X[i]*X[l] + X[j]*X[k] - X[j]*X[j] + X[j]*X[l] - X[k]*X[k])

if __name__ == "__main__":
	s1 = socket.socket()
	host = "195.154.53.62"
	port = 7412               
	
	s1.connect((host, port))
	s1.recv(1024)
	
	X = []
	
	for i in range(16):
		s1.send(b"2\n")
		time.sleep(0.1)
		initNum = int(s1.recv(1024).split(b"\n")[0], 10)
		X.append(initNum)
	
	print(X)
	
	g = [det(0,1,2,3,X), det(4,5,6,7,X), det(8,9,10,11,X), det(12,13,14,15,X)]
	m = functools.reduce(gmpy2.gcd, g)
	
	print("m = " + hex(m))
	a = ((X[2]-X[1]) * gmpy2.invert(X[1]-X[0],m)) % m
	b = (X[1] - a*X[0]) % m
	print("a=" + str(a))
	print("b=" + str(b))
	
	s1.send(b"2\n")
	time.sleep(0.1)
	num = int(s1.recv(1024).split(b"\n")[0], 10)
	print("Initial number: " + str(num))

	for i in range(10):
		
		s1.send(b"1\n")
		time.sleep(0.3)
		print(s1.recv(1024).decode())
		num = (num * a + b) % m
		print("Next number: " + str(num))
		s1.send((str(num) + "\n").encode())
	
	print(s1.recv(1024).decode())
	s1.close()


