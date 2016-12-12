QIDIR1 = /home/pi/libserialport
IDIR1 = /home/pi/libserialport
#ODIR = .
#SECONDODIR = ../package1
#_OBJ = main.o
#_SECONDOBJ = test1.o
DEPS = serialport.c linux.c linux_termios.c 
LIBS = -lrt -lpigpio -Wstrict-overflow=5

CFLAGS = -iquote$(QIDIR1) -I$(IDIR1) -Wall -pthread
#OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))
#SECONDOBJ = $(patsubst %,$(SECONDODIR)/%,$(_SECONDOBJ))
#CC=gcc


sensor_read_test_5: sensor_read_test_5.c $(DEPS)
	gcc -o $@.exe $^ $(CFLAGS) $(LIBS)

sensor_reset: sensor_reset.c 
	gcc -o $@.exe $^ $(LIBS)

sensor_write_only_test_1: sensor_write_only_test_1.c $(DEPS)
	gcc -o $@.exe $^ $(CFLAGS) $(LIBS)

#$(ODIR)/%.o: $(ODIR)/%.c $(DEPS)
#        $(CC) -c -o $@ $< $(CFLAGS)

#$(SECONDODIR)/%.o: $(SECONDODIR)/%.c $(DEPS)
#        $(CC) -c -o $@ $< $(CFLAGS)

#sensor_read_test_2: $(ODIR) $(SECONDOBJ)
#        gcc -o $@ $^ $(CFLAGS) $(LIBS)

