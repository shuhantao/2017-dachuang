import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import pandas as pd
dir_name = './FER2013'
print ('----------- no sub dir')
print ('The folder path: ', dir_name)

files = os.listdir(dir_name)
# for f in files:
#     print (dir_name + os.sep + f)
file_path = dir_name + '/'+'fer2013.csv'
# print (file_path)

data = pd.read_csv(file_path, dtype='a')
# print (data)

label = np.array(data['emotion'])
img_data = np.array(data['pixels'])
N_sample = label.size
# print label.size

Face_data = np.zeros((N_sample, 48*48))
Face_label = np.zeros((N_sample, 7), dtype=int)

for i in range(N_sample):
    x = img_data[i]
    x = np.fromstring(x, dtype=float, sep=' ')
    x_max = x.max()
    x = x/(x_max+0.0001)
#    print x_max
#    print x
    Face_data[i] = x
#     print (i,label[i])
    Face_label[i][int(label[i])] = 1
#    img_x = np.reshape(x, (48, 48))
#    plt.subplot(10,10,i+1)
#    plt.axis('off')
#    plt.imshow(img_x, plt.cm.gray)


train_num = 30000
test_num = 5000

train_x = Face_data [0:train_num, :]
train_y = Face_label [0:train_num, :]

test_x =Face_data [train_num : train_num+test_num, :]
test_y = Face_label [train_num : train_num+test_num, :]

print ("All is well")

batch_size = 500
train_batch_num = int(train_num/batch_size)
test_batch_num = int(test_num/batch_size)
train_epoch = 100

learning_rate = 0.001
# Network Parameters
n_input = 2304  # data input (img shape: 48*48)
n_classes = 7   # total classes
dropout = 0.5   # Dropout, probability to keep units

# tf Graph input

x = tf.placeholder(tf.float32, [None, n_input])
y = tf.placeholder(tf.float32, [None, n_classes])
keep_prob = tf.placeholder(tf.float32) #dropout (keep probability)

# Create some wrappers for simplicity

def conv2d(x, W, b, strides=1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)

def maxpool2d(x, k=2,s=2):
    # MaxPool2D wrapper-
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, s, s, 1],
                          padding='VALID')

# Create model
def conv_net(x, weights, biases, dropout):
    x = tf.reshape(x, shape=[-1, 48, 48, 1])
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    conv1 = maxpool2d(conv1, k=3,s=2)
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    conv2 = maxpool2d(conv2, k=3,s=2)
    conv3 = conv2d(conv2, weights['wc3'], biases['bc3'])
    conv3 = maxpool2d(conv3, k=3,s=2)
    fc1 = tf.reshape(conv3, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    fc1 = tf.nn.dropout(fc1, dropout)
    fc2 = tf.add(tf.matmul(fc1,weights['wd2']),biases['bd2'])
    fc2 = tf.nn.relu(fc2)
    fc2 = tf.nn.dropout(fc2,dropout)
    out = tf.add(tf.matmul(fc2, weights['out']), biases['out'])

    return out

# Store layers weight & bias
weights = {
    # 3x3 conv, 1 input, 128 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    # 3x3 conv, 128 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([4, 4, 32, 32])),
    # 3x3 conv, 64 inputs, 32 outputs
    'wc3': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    # fully connected,
    'wd1': tf.Variable(tf.random_normal([5*5*64, 2048])),
    'wd2': tf.Variable(tf.random_normal([2048,1024])),
    # 1024 inputs, 10 outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, n_classes]))
}


biases = {
    'bc1': tf.Variable(tf.random_normal([32])),

    'bc2': tf.Variable(tf.random_normal([32])),

    'bc3': tf.Variable(tf.random_normal([64])),

    'bd1': tf.Variable(tf.random_normal([2048])),
    'bd2': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

# Construct model
pred = conv_net(x, weights, biases, keep_prob)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.initialize_all_variables()

Train_ind = np.arange(train_num)
Test_ind = np.arange(test_num)

saver = tf.train.Saver()
with tf.Session() as sess:
    sess.run(init)
    
    for epoch in range(0, train_epoch):

        Total_test_loss = 0
        Total_test_acc = 0

        for train_batch in range (0, train_batch_num):
            sample_ind = Train_ind[train_batch * batch_size:(train_batch + 1) * batch_size]
            batch_x = train_x[sample_ind, :]
            batch_y = train_y[sample_ind, :]
            # Run optimization op (backprop)
            sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                           keep_prob: dropout})

            if train_batch % 50== 0:
                # Calculate loss and accuracy
                loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                              y: batch_y,
                                                              keep_prob: 0.4})

                print("Epoch: " + str(epoch+1) + ", Batch: "+ str(train_batch) + ", Loss= " + \
                            "{:.3f}".format(loss) + ", Training Accuracy= " + \
                            "{:.3f}".format(acc))

        # Calculate test loss and test accuracy
        for test_batch in range (0, test_batch_num):
            sample_ind = Test_ind[test_batch * batch_size:(test_batch + 1) * batch_size]
            batch_x = test_x[sample_ind, :]
            batch_y = test_y[sample_ind, :]
            test_loss, test_acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                                        y: batch_y,
                                                                        keep_prob: 1.})
            Total_test_lost = Total_test_loss + test_loss
            Total_test_acc =Total_test_acc + test_acc



        Total_test_acc = Total_test_acc/test_batch_num
        Total_test_loss =Total_test_lost/test_batch_num

        print("Epoch: " + str(epoch + 1) + ", Test Loss= " + \
                      "{:.3f}".format(Total_test_loss) + ", Test Accuracy= " + \
                      "{:.3f}".format(Total_test_acc))
    save_path = saver.save(sess, "/tmp/model.ckpt")

plt.subplot(2,1,1)
plt.ylabel('Test loss')
plt.plot(Total_test_loss, 'r')
plt.subplot(2,1,2)
plt.ylabel('Test Accuracy')
plt.plot(Total_test_acc, 'r')


print ("All is well")
plt.show()