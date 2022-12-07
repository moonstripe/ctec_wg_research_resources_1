import matplotlib.pyplot as plt
from scipy import stats
import numpy as np


class EstablishingTimelineGrapher:
    def __init__(self):
        self.pre_dates = ['2020-09-21','2020-09-28','2020-10-05','2020-10-12','2020-10-19','2020-10-26','2020-11-16','2020-11-30','2020-12-07','2020-12-14','2020-12-28','2021-01-04','2021-01-11','2021-01-18','2021-01-25','2021-02-01','2021-02-08','2021-02-15','2021-02-22','2021-03-01','2021-03-15','2021-03-29','2021-04-05','2021-04-12','2021-04-19','2021-05-03','2021-05-10','2021-05-17','2021-05-24','2021-05-31','2021-06-07','2021-06-14','2021-06-21']
        self.during_dates = ['2021-06-28','2021-07-05','2021-07-12','2021-07-19','2021-08-02','2021-08-09','2021-08-16','2021-08-23','2021-08-30','2021-09-06','2021-09-20','2021-09-27','2021-10-04','2021-10-11','2021-10-18','2021-10-25','2021-11-01','2021-11-08','2021-11-15','2021-11-22','2021-11-29','2021-12-06','2021-12-13','2021-12-20','2021-12-27','2022-01-03','2022-01-10','2022-01-17','2022-01-24','2022-01-31','2022-02-07','2022-02-14','2022-02-21']
        self.post_dates = ['2022-02-28','2022-03-07','2022-03-14','2022-03-21','2022-03-28','2022-04-04','2022-04-11','2022-04-18','2022-04-25','2022-05-02','2022-05-09','2022-05-16','2022-05-23','2022-05-30','2022-06-06','2022-06-13','2022-06-20','2022-06-27','2022-07-04','2022-07-11','2022-07-18','2022-07-25','2022-08-01','2022-08-08','2022-08-15','2022-08-22','2022-08-29','2022-09-05','2022-09-12','2022-09-19','2022-09-26','2022-10-03','2022-10-10']
        self.time_values = self.pre_dates + self.during_dates + self.post_dates
        self.pre_values = [-0.344,-0.6160606061,-0.4125,-0.7166666667,-0.4447368421,-0.311,-0.2875,-0.2633333333,-0.6265217391,-0.54625,0.1314285714,-0.3755172414,-0.5726315789,-0.045,-0.733125,-0.482,-0.1564705882,-0.5978125,-0.066,-0.2575,-0.6866666667,-0.07526315789,-0.61,-0.3278947368,0,-0.4355555556,-0.4347826087,-0.04711864407,-0.2333333333,0.106,-0.3592857143,-0.194,-0.4736363636]
        self.during_values = [0.1231372549,-0.6751428571,-0.29,0.3933333333,-0.45,-0.31,0.07111111111,-0.381452514,-0.20640625,-0.1833333333,-0.5671428571,-0.454,-0.4565789474,-0.4,-0.18,0.1059259259,-0.2582857143,-0.4964485981,0.025,-0.67625,-0.2714814815,-0.1497979798,-0.1651428571,-0.3827027027,0.2368235294,-0.418671875,-0.2372131148,0.26,-0.1852941176,0.1222222222,-0.3069354839,-0.2955102041,0.4317647059]
        self.post_values = [-0.4613207547,-0.3971875,-0.4191525424,-0.4871317829,-0.5041121495,-0.4035665914,-0.417955707,-0.4067877095,-0.4661083744,-0.1737171717,-0.2026857143,-0.5126986301,-0.2531180401,-0.312875,-0.5647746244,-0.3404463519,-0.4094552929,-0.1604674457,-0.3647384615,-0.2955807365,-0.4262330097,-0.3274840358,-0.31640625,-0.5311764706,-0.512746114,-0.4430943396,-0.210967033,-0.3776859504,-0.3781045082,-0.3984771574,-0.4068914694,-0.1769157393,-0.2355857899]
        self.plot_values = self.pre_values + self.during_values + self.post_values
        self.pre_mean = np.mean(self.pre_values)
        self.during_mean = np.mean(self.during_values)
        self.post_mean = np.mean(self.post_values)

    def test_data(self):
        # total len of pre during and post should be equal
        print(len(self.time_values) == len(self.plot_values))

    def draw_plot(self):
        plt.clf()

        plt.figure(figsize=(52, 36), dpi=80)

        fig, axs = plt.subplots(2, 2, constrained_layout=True)
        fig.set_figheight(6)
        fig.set_figwidth(8)
        fig.set_dpi(80)


        axs[0, 0].plot(self.time_values, self.plot_values, 'k', label="_nolegend_", linestyle="solid")
        z = np.polyfit(np.arange(0, 99, 1), self.plot_values, 1)
        p = np.poly1d(z)
        axs[0, 0].plot(np.arange(0, 99, 1), p(np.arange(0, 99, 1)), 'k', label="trendline", linestyle="solid")
        axs[0, 0].set_title('Total Time Frame')
        axs[0, 0].set_ylim([-1, 1])
        axs[0, 0].set_ylabel("Weighted Differential")
        axs[0, 0].set_xlabel("Week")
        axs[0, 0].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array0_0 = self.time_values[::25]
        axs[0, 0].set_xticks(label_array0_0)
        axs[0, 0].legend(frameon=False)
        axs[0, 0].grid(axis='y')


        axs[0, 1].plot(self.pre_dates, self.pre_values, 'r', label="_nolegend_", linestyle="solid")
        z = np.polyfit(np.arange(0, 33, 1), self.pre_values, 1)
        p = np.poly1d(z)
        axs[0, 1].plot(np.arange(0, 33, 1), p(np.arange(0, 33, 1)), 'r', label="trendline", linestyle="solid")
        axs[0, 1].set_title('Before')
        axs[0, 1].set_ylim([-1, 1])
        axs[0, 1].set_ylabel("Weighted Differential")
        axs[0, 1].set_xlabel("Week")
        axs[0, 1].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array0_1 = self.pre_dates[::10]
        axs[0, 1].set_xticks(label_array0_1)
        axs[0, 1].legend(frameon=False)
        axs[0, 1].grid(axis='y')

        axs[1, 0].plot(self.during_dates, self.during_values, 'g', label="_nolegend_", linestyle="solid")
        z = np.polyfit(np.arange(0, 33, 1), self.during_values, 1)
        p = np.poly1d(z)
        axs[1, 0].plot(np.arange(0, 33, 1), p(np.arange(0, 33, 1)), 'g', label="trendline", linestyle="solid")
        axs[1, 0].set_title('Between')
        axs[1, 0].set_ylim([-1, 1])
        axs[1, 0].set_ylabel("Weighted Differential")
        axs[1, 0].set_xlabel("Week")
        axs[1, 0].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array1_0 = self.during_dates[::10]
        axs[1, 0].set_xticks(label_array1_0)
        axs[1, 0].legend(frameon=False)
        axs[1, 0].grid(axis='y')

        axs[1, 1].plot(self.post_dates, self.post_values, 'b', label="_nolegend_", linestyle="solid")
        z = np.polyfit(np.arange(0, 33, 1), self.post_values, 1)
        p = np.poly1d(z)
        axs[1, 1].plot(np.arange(0, 33, 1), p(np.arange(0, 33, 1)), 'b', label="trendline", linestyle="solid")
        axs[1, 1].set_title('After')
        axs[1, 1].set_ylim([-1, 1])
        axs[1, 1].set_ylabel("Weighted Differential")
        axs[1, 1].set_xlabel("Week")
        axs[1, 1].tick_params(axis="x", size = 8, labelrotation = 15)
        label_array1_1 = self.post_dates[::10]
        axs[1, 1].set_xticks(label_array1_1)
        axs[1, 1].legend(frameon=False)
        axs[1, 1].grid(axis='y')

        plt.savefig('images/establishing.png')


if __name__ == "__main__":
    etg = EstablishingTimelineGrapher()
    etg.test_data()
    etg.draw_plot()