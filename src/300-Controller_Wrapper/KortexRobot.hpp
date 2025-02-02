// KortexRobot.hpp

#ifndef KORTEXROBOT_HPP
#define KORTEXROBOT_HPP

#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <fstream>
#include <numeric>
#include <sstream>
#include <iomanip>

#include <stdio.h>
#include <csignal>

#include <KDetailedException.h>

#include <BaseClientRpc.h>
#include <BaseCyclicClientRpc.h>
#include <ControlConfigClientRpc.h>
#include <ActuatorConfigClientRpc.h>
#include <DeviceConfigClientRpc.h>
#include <SessionClientRpc.h>
#include <SessionManager.h>

#include <RouterClient.h>
#include <TransportClientTcp.h>
#include <TransportClientUdp.h>

#include <google/protobuf/util/json_util.h>

#include "utilities.h"
#include "pid.cpp"

#if defined(_MSC_VER)
#include <Windows.h>
#else
#include <unistd.h>
#endif
#include <time.h>


#define PORT 10000
#define PORT_REAL_TIME 10001
#define DURATION 100             // Network timeout (seconds)
#define X_MIN 0.26            // Network timeout (seconds)
#define X_MAX 0.6             // Network timeout (seconds)
#define Y_MIN -0.28             // Network timeout (seconds)
#define Y_MAX 0.28             // Network timeout (seconds)

namespace k_api = Kinova::Api;

const auto ACTION_WAITING_TIME = std::chrono::seconds(1);
float time_duration = DURATION; // Duration of the example (seconds)

class KortexRobot
{
private:
    std::string ip_address;
    std::string username;
    std::string password;
    bool running_demo;
    

    k_api::TransportClientTcp* transport;
    k_api::RouterClient* router;
    k_api::TransportClientUdp* transport_real_time;
    k_api::RouterClient* router_real_time;

    k_api::Session::CreateSessionInfo create_session_info;

    k_api::SessionManager* session_manager;
    k_api::SessionManager* session_manager_real_time;

    k_api::Base::BaseClient* base;
    k_api::BaseCyclic::BaseCyclicClient* base_cyclic;

    
    k_api::ActuatorConfig::ActuatorConfigClient* actuator_config;
    k_api::DeviceConfig::DeviceConfigClient* device_config;
	k_api::ControlConfig::ControlConfigClient* control_config;


	std::function<void(k_api::Base::ActionNotification)>
	check_for_end_or_abort(bool& finished);
	void printException(k_api::KDetailedException& ex);

	int64_t GetTickUs();

public:
    KortexRobot(const std::string& ip_address, const std::string& username, const std::string& password, bool inputdemo = false);
	void go_to_point(const std::string& actionName);
	void connect();
	void disconnect();
    ~KortexRobot();
    void set_actuator_control_mode(int mode_control, int actuator_indx = -1);
	void writing_mode();
	vector<vector<float>> move_cartesian(std::vector<std::vector<float>> waypointsDefinition, bool repeat = false,
					float kTheta_x = 180.0f, float kTheta_y = 0.0f, float kTheta_z = 90.0f, bool joints_provided = false);

	std::vector<std::vector<float>> convert_points_to_angles(std::vector<vector<float>> target_points);
	
    std::vector<std::vector<float>> read_csv(const std::string &filename, int scale = 1000);
    std::vector<std::vector<float>> convert_csv_to_cart_wp(std::vector<std::vector<float>> csv_points, 
                                                                        float kTheta_x, float kTheta_y, 
                                                                        float kTheta_z);

    void calculate_bias(std::vector<float> first_waypoint);
    void output_arm_limits_and_mode();

    const vector<float> actuator_pos_tolerance = {0.085, 0.105, 0.105, 0.105, 0.105, 0.105};
    const vector<int> actuator_control_types = {1,1,1,1,1,0};
	const vector<float> command_max = {100.0, 30, 30.0, 15.0, 30, 25.0}; 
	const vector<float> command_min = {-100.0, -30.0, -30.0, -15.0, -30, -25.0}; 
	const vector<float> step_change_limit = {20.0, 30, 2, 20.0, 20.0, 20.0}; 
    std::vector<float> motor_command= {10.0f, 10.0f, 10.0f, 10.0f, 10.0f, 10.0f}; //Vector of current_velocities/torques to use in calculation for next command

	void init_pids();
	void get_gain_values(const std::string& filename);

    vector<float> altered_origin;
    vector<float> bais_vector;

    int actuator_count;
    vector<Pid_Loop> pids;

	const vector<float> surface_cords = {0.455,0,0.115};
	void find_paper();
    // Plotting and performance functions
    vector<float> measure_joints(k_api::BaseCyclic::Feedback base_feedback, int64_t start_time);
	int start_plot();
    void plot(vector<vector<float>> expected_data,vector<vector<float>> measured_data);
    int create_plot_file(string file_name, vector<vector<float>> data);
    vector<float> rms_error(vector<vector<float>> expected, vector<vector<float>> measured);
    vector<vector<float>> generate_log(const std::string& filename, vector<vector<float>>data);
    void output_joint_values_to_csv(std::vector<std::vector<float>> joint_angles, const std::string& filename);
    void execute_demo();
    void set_origin_point();

	FILE *gnu_plot;

protected:
	//data
    

};

#endif // KORTEXROBOT_HPP

