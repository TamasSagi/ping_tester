import platform
import subprocess
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from collections import deque
from itertools import count
from matplotlib.animation import FuncAnimation


class PingTester:
    """
    This class constantly pings the given host (www.google.com by default) and draws a line graph
    based on the latencies.
    """

    def __init__(self, host="www.google.com", sample_size=50) -> None:
        self.host = host
        self.idx = count(start=1)
        self.pings = deque([], sample_size)
        self.indexes = deque([], sample_size)

    def ping_host(self) -> None:
        """
        Pings the host once and returns the latency.
        """
        os_type = platform.system().lower()

        if os_type == "windows":
            ping = self.ping_windows("-n", "1")
        elif os_type == "linux":
            ping = self.ping_linux("-4", "-c", "1")
        else:
            raise NotImplementedError(f"Ping host is not implemented for '{os_type}'")

        if ping:
            self.pings.append(ping)
            self.indexes.append(next(self.idx))

    def ping_windows(self, *args) -> None:
        # Run the ping command and read stdout
        response = subprocess.run(["ping", *args, self.host], capture_output=True).stdout.decode("utf-8")

        # Check if the pinging was succesfull
        if "Reply from" in response:
            # As I am pinging the host once I just parse the average latency value
            # Replace Average with Minimum or Maximum if you want those values
            return float(response.split("Average = ")[1].split("ms")[0])

    def ping_linux(self, *args) -> None:
        # Run the ping command and read stdout
        response = subprocess.run(["ping", *args, self.host], capture_output=True).stdout.decode("utf-8")

        if "1 received" in response:
            return float(response.split("time=")[1].split(" ms")[0])

    def draw(self) -> None:
        """
        Creates the matplotlib figure and axes and starts the interactive plotting.
        """
        # Set plotting styles
        with plt.xkcd():
            plt.style.use("fivethirtyeight")

            figure, self.ax = plt.subplots(1, 1)
            figure.set_figwidth(12)
            figure.set_figheight(5)

            _ = FuncAnimation(figure, self.step, interval=100)

            plt.tight_layout()
            plt.show()

    def step(self, *args) -> None:
        """
        Pings the host, sets some drawing parameters and draws the line graph.
        """
        self.ping_host()

        # Clear the current axes
        plt.cla()

        # Adjust the plot a bit right so the Y label can fit
        plt.subplots_adjust(left=0.07)

        # Set the limits, labels, title and add units to the Y ticks
        self.ax.set_ylim(0, max(self.pings) * 1.5)
        self.ax.set_xlabel("Index", fontweight="bold", fontsize=14)
        self.ax.set_ylabel("Latency [ms]", fontweight="bold", fontsize=14)
        self.ax.set_title(
            "Ping Test (max:{}, min:{}, avg:{:.2f})".format(
                max(self.pings), min(self.pings), sum(self.pings) / len(self.pings)
            ),
            fontweight="bold",
            fontsize=18,
        )
        self.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%d ms"))

        # Draw the lines
        plt.plot(self.indexes, self.pings, linewidth=1, marker="o", markersize=3, color="black")


if __name__ == "__main__":
    ping_tester = PingTester()
    ping_tester.draw()
