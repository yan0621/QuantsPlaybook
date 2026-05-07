def standardlize(data, inf2nan=True, axis=1):
    """标准化函数

    输入: data: pd.Series/np.array/pd.DataFrame，待标准化的序列
          inf2nan=True:  bool，是否将 np.inf 和 -np.inf 替换成 np.nan
          axis=1:  0 或 1，如果 data 为 pd.DataFrame，沿哪个方向做标准化
                   0 为对每列做标准化，1 为对每行做标准化

    输出: pd.Series  标准化后的序列
    """

    from .preprocess import standardlize

    return standardlize(data, inf2nan=inf2nan, axis=axis)


zscore = standardlize


def winsorize(
    data, scale=None, range=None, qrange=None, inclusive=True, inf2nan=True, axis=1
):
    """缩尾函数

    将位于边界之外的极值替换为边界值/nan

    输入:
        data: pd.Series/np.array  待缩尾的序列
        scale:  float  标准差倍数，与 range，qrange 三选一，不可同时使用。
                       会将位于 [mu - scale * sigma, mu + scale * sigma] 边界之外的值替换为边界值
        range:  list of float  绝对界限，与 scale，qrange 三选一，不可同时使用。
                               缩尾的上下边界。
        qrange:  list of float  分位数界限，与 scale，range 三选一，不可同时使用。
                                缩尾的上下分位数边界。
        inclusive bool  是否将位于边界之外的值替换为边界值，默认为 True
                        如果为 True，则将边界之外的值替换为边界值，否则则替换为 np.nan
        inf2nan bool  是否将 np.inf 和 -np.inf 替换成 np.nan，默认为 True
                      如果为 True，在缩尾之前会先将 np.inf 和 -np.inf 替换成 np.nan
                      缩尾的时候不会考虑 np.nan，
                      否则 inf 被认为是在上界之上，-inf 被认为在下界之下
        axis 0 或 1  如果 data 为 pd.DataFrame，沿哪个方向做标准化，默认为 1
                     0 为对每列做缩尾，1 为对每行做缩尾

    输出: pd.Series/np.array，缩尾后的序列

    说明: 1. 这里 mu 为 data 的均值，sigma 为 data 的标准差
         2. 计算时不考虑 nan
         3. 替换时 inf 被认为是在上界之外，-inf 被认为在下界之外

    举例: winsorize(np.array([1,2,3,4,5,6,7,8,9,10]), scale=1, inclusive=False)
          返回 array([nan, nan, 3., 4., 5., 6., 7., 8., nan, nan])

          winsorize(np.array([1,2,3,4,5,6,7,8,9,10]), qrange=[0.159, 0.841])
          返回 array([2., 2., 3., 4., 5., 6., 7., 8., 9., 9.])

          winsorize(np.array([1,2,3,4,5,6,7,8,9,10,np.nan,np.inf]),
                    qrange=[0.15, 0.85], inf2nan=False)
          返回 array([2., 2., 3., 4., 5., 6., 7., 8., 9., 10., nan, 10.])
    """

    from .utils import affirm

    affirm(
        ((scale is not None) + (range is not None) + (qrange is not None)) == 1,
        "winsorize 函数中 scale 参数, range 参数和 qrange 参数应有且只有一个不为 None",
    )

    from .preprocess import winsorize

    return winsorize(
        data,
        scale=scale,
        range=range,
        qrange=qrange,
        inclusive=inclusive,
        inf2nan=inf2nan,
        axis=axis,
    )


def winsorize_med(data, scale=1, inclusive=True, inf2nan=True, axis=1):
    """中位数缩尾函数

    将位于边界之外的极值替换为边界值/nan

    输入:
        data: pd.Series/np.array  待缩尾的序列
        scale:  float  倍数，默认为 1.0
                       会将位于
                         [med - scale * distance, med + scale * distance]
                       边界之外的值替换为边界值/np.nan
        inclusive bool  是否将位于边界之外的值替换为边界值，默认为 True
                        如果为 True，则将边界之外的值替换为边界值，否则则替换为 np.nan
        inf2nan bool  是否将 np.inf 和 -np.inf 替换成 np.nan，默认为 True
                      如果为 True，在缩尾之前会先将 np.inf 和 -np.inf 替换成 np.nan
                      缩尾的时候不会考虑 np.nan，
                      否则 inf 被认为是在上界之上，-inf 被认为在下界之下
        axis 0 或 1  如果 data 为 pd.DataFrame，沿哪个方向做标准化，默认为 1
                     0 为对每列做缩尾，1 为对每行做缩尾

    输出: pd.Series  缩尾后的序列

    说明: 1. med 为 data 的中位数
            distance 为 abs(data - med) 的中位数
         2. 计算时不考虑 nan
         3. 替换时 inf 被认为是在上界之外，-inf 被认为在下界之外

    举例: winsorize_med(np.array([1,2,3,4,5,6,7,8,9,10,np.nan]), scale=1)
          返回 np.array([3,3,3,4,5,6,7,8,8,8,np.nan])
          这里 med 为 5.5，sigma 为 2.5
    """

    from .preprocess import winsorize_med

    return winsorize_med(
        data, scale=scale, inclusive=inclusive, inf2nan=inf2nan, axis=axis
    )