import numpy as np
import math
import sys
import cv2


def integral(img):
    """
    计算图像的积分和平方积分
    :param img:Mat--- 输入待处理图像
    :return:integral_sum, integral_sqrt_sum：Mat--- 积分图和平方积分图
    （也就是像素点的和和sqrt后的积分图）
    """
    integral_sum = np.zeros((img.shape[0], img.shape[1]), dtype=np.int32)
    integral_sqrt_sum = np.zeros((img.shape[0], img.shape[1]), dtype=np.int32)

    rows, cols = img.shape[0], img.shape[1]
    for r in range(rows):
        sum = 0
        sqrt_sum = 0
        for c in range(cols):
            sum += img[r][c]

            sqrt_sum += math.sqrt(img[r][c])

            if r == 0:
                integral_sum[r][c] = sum
                integral_sqrt_sum[r][c] = sqrt_sum
            else:
                integral_sum[r][c] = sum + integral_sum[r - 1][c]
                integral_sqrt_sum[r][c] = sqrt_sum + integral_sqrt_sum[r - 1][c]

    return integral_sum, integral_sqrt_sum


def sauvola(img, k=0.1, kernerl=(31, 31)):
    """
    sauvola阈值法。
    根据当前像素点邻域内的灰度均值与标准方差来动态计算该像素点的阈值
    :param img:Mat--- 输入待处理图像
    :param k:float---修正参数,一般0<k<1
    :param kernerl:set---窗口大小
    :return:img:Mat---阈值处理后的图像
    """

    # kernerl 为选择框的大小
    if kernerl[0] % 2 != 1 or kernerl[1] % 2 != 1:
        raise ValueError('kernerl元组中的值必须为奇数,'
                         '请检查kernerl[0] or kernerl[1]是否为奇数!!!')

    # 计算积分图和积分平方和图
    integral_sum, integral_sqrt_sum = integral(img)
    # integral_sum, integral_sqrt_sum = cv2.integral2(img)
    # integral_sum=integral_sum[1:integral_sum.shape[0],1:integral_sum.shape[1]]
    # integral_sqrt_sum=integral_sqrt_sum[1:integral_sqrt_sum.shape[0],1:integral_sqrt_sum.shape[1]]

    # 创建图像
    rows, cols = img.shape
    diff = np.zeros((rows, cols), np.float64)
    sqrt_diff = np.zeros((rows, cols), np.float64)
    mean = np.zeros((rows, cols), np.float64)
    threshold = np.zeros((rows, cols), np.float64)
    std = np.zeros((rows, cols), np.float64)

    whalf = kernerl[0] >> 1  # 计算领域类半径的一半

    for row in range(rows):
        # print('第{}行处理中...'.format(row))
        for col in range(cols):
            xmin = max(0, row - whalf)
            ymin = max(0, col - whalf)
            xmax = min(rows - 1, row + whalf)
            ymax = min(cols - 1, col + whalf)

            area = (xmax - xmin + 1) * (ymax - ymin + 1)
            if area <= 0:
                sys.exit(1)

            if xmin == 0 and ymin == 0:
                diff[row, col] = integral_sum[xmax, ymax]
                sqrt_diff[row, col] = integral_sqrt_sum[xmax, ymax]
            elif xmin > 0 and ymin == 0:
                diff[row, col] = integral_sum[xmax, ymax] - integral_sum[xmin - 1, ymax]
                sqrt_diff[row, col] = integral_sqrt_sum[xmax, ymax] - integral_sqrt_sum[xmin - 1, ymax]
            elif xmin == 0 and ymin > 0:
                diff[row, col] = integral_sum[xmax, ymax] - integral_sum[xmax, ymax - 1]
                sqrt_diff[row, col] = integral_sqrt_sum[xmax, ymax] - integral_sqrt_sum[xmax, ymax - 1]
            else:
                diagsum = integral_sum[xmax, ymax] + integral_sum[xmin - 1, ymin - 1]
                idiagsum = integral_sum[xmax, ymin - 1] + integral_sum[xmin - 1, ymax]
                diff[row, col] = diagsum - idiagsum

                sqdiagsum = integral_sqrt_sum[xmax, ymax] + integral_sqrt_sum[xmin - 1, ymin - 1]
                sqidiagsum = integral_sqrt_sum[xmax, ymin - 1] + integral_sqrt_sum[xmin - 1, ymax]
                sqrt_diff[row, col] = sqdiagsum - sqidiagsum

            mean[row, col] = diff[row, col] / area
            std[row, col] = math.sqrt((sqrt_diff[row, col] - math.sqrt(diff[row, col]) / area) / (area - 1))
            threshold[row, col] = mean[row, col] * (1 + k * ((std[row, col] / 128) - 1))

            if img[row, col] < threshold[row, col]:
                img[row, col] = 255
            else:
                img[row, col] = 0

    return img


if __name__ == '__main__':
    Path = "/Users/rune/PycharmProjects/RNN_book/Test_cv/Test_images/Warped.jpeg"
    img = cv2.imread(Path)
    gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    Sauvola = sauvola(gray1)
    ret, binary = cv2.threshold(gray2, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("img", img)
    cv2.imshow("Sav", Sauvola)
    cv2.imshow("bin", binary)
    cv2.waitKey(0)
