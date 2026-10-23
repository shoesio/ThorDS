#include <chrono>
#include <ctime>
#include <cstdlib>
#include <cmath>
#include <cstdint>
#include <cassert>
#include <iostream>
using u64=uint64_t;using s64=int64_t;
#define UNREACHABLE_MSG(...) std::abort()
namespace Settings {
enum class InitClock { SystemTime, FixedTime };
template<class T> struct Setting { T value{}; T GetValue() const {return value;} };
struct Values {Setting<InitClock> init_clock;Setting<s64> init_time_offset;Setting<u64> init_time;} values;
}
struct TestClock {static inline int64_t ms=1792344000123;static auto now(){return std::chrono::system_clock::time_point(std::chrono::milliseconds(ms));}};
namespace Core {struct MovieMock {u64 value=0;u64 GetOverrideInitTime(){return value;}};struct System {MovieMock movie;MovieMock& Movie(){return movie;}static System& GetInstance(){static System x;return x;}};}
namespace SharedPage {
struct Timing {std::chrono::microseconds elapsed{};auto GetGlobalTimeUs() const{return elapsed;}};
struct Handler {std::chrono::seconds init_time;Timing timing;u64 GetSystemTimeSince2000() const;};
static std::chrono::milliseconds GetHostTime() {
    auto now = TestClock::now();
    // If the system time is in daylight saving, we give an additional hour to console time
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    std::tm* now_tm = std::localtime(&now_time_t);
    if (now_tm && now_tm->tm_isdst > 0)
        now = now + std::chrono::hours(1);

    // add the offset
    s64 init_time_offset = Settings::values.init_time_offset.GetValue();
    long long days_offset = init_time_offset / 86400;
    long long days_offset_in_seconds = days_offset * 86400; // h/m/s truncated
    unsigned long long seconds_offset =
        std::abs(init_time_offset) - std::abs(days_offset_in_seconds);

    now = now + std::chrono::seconds(seconds_offset);
    now = now + std::chrono::seconds(days_offset_in_seconds);
    return std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch());
}

std::chrono::seconds GetInitTime(u64 override_init_time) {
    if (override_init_time != 0) {
        // Override the clock init time with the one in the movie
        return std::chrono::seconds(override_init_time);
    }

    switch (Settings::values.init_clock.GetValue()) {
    case Settings::InitClock::SystemTime:
        return std::chrono::duration_cast<std::chrono::seconds>(GetHostTime());
    case Settings::InitClock::FixedTime:
        return std::chrono::seconds(Settings::values.init_time.GetValue());
    default:
        UNREACHABLE_MSG("Invalid InitClock value ({})", Settings::values.init_clock.GetValue());
    }
}

u64 Handler::GetSystemTimeSince2000() const {
    // The real 3DS RTC advances while the lid is closed. Emulated ticks
    // stop during host suspend and lag behind at less than full speed.
    // Fixed clocks and movie time overrides retain deterministic timing.
    const bool use_host_clock =
        Settings::values.init_clock.GetValue() == Settings::InitClock::SystemTime &&
        Core::System::GetInstance().Movie().GetOverrideInitTime() == 0;
    const std::chrono::milliseconds now = use_host_clock
        ? GetHostTime()
        : init_time + std::chrono::duration_cast<std::chrono::milliseconds>(timing.GetGlobalTimeUs());

    // 3DS system does't allow user to set a time before Jan 1 2000,
    // so we use it as an auxiliary epoch to calculate the console time.
    std::tm epoch_tm;
    epoch_tm.tm_sec = 0;
    epoch_tm.tm_min = 0;
    epoch_tm.tm_hour = 0;
    epoch_tm.tm_mday = 1;
    epoch_tm.tm_mon = 0;
    epoch_tm.tm_year = 100;
    epoch_tm.tm_isdst = 0;
    s64 epoch = std::mktime(&epoch_tm) * 1000;

    // Only when system time is after 2000, we set it as 3DS system time
    if (now.count() > epoch) {
        return now.count() - epoch;
    } else {
        return 0;
    }
}


}
int main(){
 setenv("TZ","UTC",1);tzset();
 using namespace std::chrono;
 Settings::values.init_clock.value=Settings::InitClock::SystemTime;
 SharedPage::Handler h{SharedPage::GetInitTime(0),{}};
 auto start=h.GetSystemTimeSince2000();TestClock::ms+=120000;
 assert(h.GetSystemTimeSince2000()-start==120000); // suspend: no guest tick progress
 h.timing.elapsed=seconds(10);assert(h.GetSystemTimeSince2000()-start==120000); // slow emulation
 Settings::values.init_time_offset.value=86400;assert(h.GetSystemTimeSince2000()-start==86520000);
 Settings::values.init_time_offset.value=0;
 Settings::values.init_clock.value=Settings::InitClock::FixedTime;
 auto fixed=h.GetSystemTimeSince2000();TestClock::ms+=3600000;assert(h.GetSystemTimeSince2000()==fixed);
 h.timing.elapsed+=seconds(3);assert(h.GetSystemTimeSince2000()-fixed==3000);
 Settings::values.init_clock.value=Settings::InitClock::SystemTime;Core::System::GetInstance().movie.value=123;
 auto movie=h.GetSystemTimeSince2000();TestClock::ms+=3600000;assert(h.GetSystemTimeSince2000()==movie);
 h.timing.elapsed+=seconds(2);assert(h.GetSystemTimeSince2000()-movie==2000);
 std::cout<<"Clock tests passed: sleep gap, slow emulation, millisecond precision, date offset, fixed time and movie override.\n";
}
