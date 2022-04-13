import time
import matplotlib.pyplot as plt
import GetContents


def benchMarkingParseContgent(valid_domain_names):
    times = {"correct" : [], "errored" : []}

    counter = 1
    for i in range(4):
        print("outer circle: ", i)
        for j in range(100):
            print("inner circle: ", j)
            start_time = time.perf_counter_ns()
            try:
                web = GetContents.WebSiteContent(valid_domain_names[i * 100 + j])
                web.parseContent()

                end_time = time.perf_counter_ns()
                times['correct'].append(end_time - start_time)
            except:
                end_time = time.perf_counter_ns()
                times['errored'].append(end_time - start_time)
                print("error:", counter, "<-->", valid_domain_names[i * 100 + j])
                counter += 1


    fig, ax = plt.subplots()
    ax.boxplot(times.values())
    ax.set_xticklabels(times.keys())
    plt.show()
