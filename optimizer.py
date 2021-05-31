from casadi import *
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

class Optimizer:
    def __init__(self,k_d=0.0155,k_l=5.0269,k_w=5.0269):
        y = MX.sym('y',8)
        u = MX.sym('u',4)
        self.y = y
        self.u = u
        g=9.81
        self.lambd=0
        self.gamma=0
        self.theta=0
        self.k_d=k_d
        self.k_l=k_l
        self.k_w=k_w
        self.target = [0,0,0]

        ydot0=y[3] * u[3]
        ydot1=y[4] * u[3]
        ydot2=y[5] * u[3]
        ydot3=(self.k_l*y[7]*(np.sin(self.lambd)*np.sin(self.gamma)*y[5]-np.cos(self.lambd)*y[4])-self.k_d*y[6]*y[3]) * u[3]
        ydot4=(self.k_l*y[7]*(np.sin(self.lambd)*np.cos(self.gamma)*y[5]-np.cos(self.lambd)*y[3])-self.k_d*y[6]*y[4]) * u[3]
        ydot5=(self.k_l*y[7]*(np.sin(self.lambd)*np.cos(self.gamma)*y[4]-np.sin(self.lambd)*np.sin(self.gamma)*y[3])-self.k_d*y[6]*y[5]-g) * u[3]
        ydot6=(self.k_l*y[7]*((np.sin(self.lambd)*np.sin(self.gamma)*y[5]-np.cos(self.lambd)*y[4])+(np.sin(self.lambd)*np.cos(self.gamma)*y[5]-np.cos(self.lambd)*y[3])+(np.sin(self.lambd)*np.cos(self.gamma)*y[4]-np.sin(self.lambd)*np.sin(self.gamma)*y[3]))/(y[6]) -self.k_d*(y[3]+y[4]+y[5])) * u[3]
        ydot7=(-self.k_w*y[7]*y[7]) * u[3]
        self.ydot = vertcat(ydot0,ydot1,ydot2,ydot3,ydot4,ydot5,ydot6,ydot7)

    def find_initvalues_spin(self,target):
        self.target=target
        print("Desired target: ", target)

        # Make integrator -  No Lagrangian
        dae={'x':self.y, 'p':self.u, 'ode':self.ydot}

        opts = {'tf':1}
        F = integrator('F', 'cvodes', dae, opts)

        # Initial state
        U0 = MX.sym('U0',4)
        w = [U0]
        lbw = [1,5*np.pi/180,-1,0]
        ubw = [27,45*np.pi/180,1,np.inf]
        w0 = [10,45*np.pi/180,0,2]

        #How to define terminal constraints and Mayer costfunction?
        
        dx_0=U0[0]*np.cos(U0[1])*np.sin(self.theta)
        dy_0=U0[0]*np.cos(U0[1])*np.cos(self.theta)
        dz_0=U0[0]*np.sin(U0[1])

        X_init = vertcat(0,0.1,0.1,dx_0,dy_0,dz_0,U0[0],U0[2])
        Fk = F(x0=X_init,p=U0)
        X_end = Fk['xf']
        
        dirgain=[1,10,1]
        J=dirgain[0]*(X_end[0]-self.target[0])**2 + dirgain[1]*(X_end[1]-self.target[1])**2 + dirgain[2]*(X_end[2]-self.target[2])**2

        g=[X_end[0],X_end[1],X_end[2]]
        lbg=[self.target[0],self.target[1],self.target[2]]
        ubg=[self.target[0],self.target[1],self.target[2]]

        prob = {'f': J, 'x': vertcat(*w),'g': vertcat(*g)}
        opts={
            "ipopt.acceptable_tol":1e-8,
            "ipopt.acceptable_obj_change_tol":1e-6,
            "ipopt.print_level":1
        }

        solver = nlpsol('solver', 'ipopt', prob,opts)
        sol = solver(x0=w0, lbx=lbw, ubx=ubw, lbg=lbg, ubg=ubg)
        sol_speed = sol['x'][0]
        sol_angle= sol['x'][1]
        sol_spin = sol['x'][2]
        sol_tf = sol['x'][3]
        #print("Landed on: ", X_end)
        solution = [float(sol_speed),float(sol_angle)*180/np.pi,float(sol_spin),float(sol_tf)]
        print("The optimal solution for speed, angle, spin, tf is:", solution)
        return float(sol_speed),float(sol_angle),float(sol_spin),float(sol_tf)

    def calculate_real_speed(self,landingpoint, setspeed, angle, spin, tf):
        self.target=landingpoint
        print("Desired target: ", landingpoint)

        # Make integrator -  No Lagrangian
        dae={'x':self.y, 'p':self.u, 'ode':self.ydot}

        opts = {'tf':1}
        F = integrator('F', 'cvodes', dae, opts)

        # Initial state
        U0 = MX.sym('U0',4)
        w = [U0]
        lbw = [1,5*np.pi/180,-1,0]
        ubw = [27,45*np.pi/180,1,np.inf]
        w0 = [setspeed,angle*np.pi/180,spin,tf]

        #How to define terminal constraints and Mayer costfunction?
        
        dx_0=U0[0]*np.cos(U0[1])*np.sin(self.theta)
        dy_0=U0[0]*np.cos(U0[1])*np.cos(self.theta)
        dz_0=U0[0]*np.sin(U0[1])


        X_init = vertcat(0,0.1,0.1,dx_0,dy_0,dz_0,U0[0],U0[2])
        Fk = F(x0=X_init,p=U0)
        X_end = Fk['xf']
        
        dirgain=[1,10,1]
        J=dirgain[0]*(X_end[0]-self.target[0])**2 + dirgain[1]*(X_end[1]-self.target[1])**2 + dirgain[2]*(X_end[2]-self.target[2])**2

        g=[X_end[0],X_end[1],X_end[2]]
        lbg=[self.target[0],self.target[1],self.target[2]]
        ubg=[self.target[0],self.target[1],self.target[2]]

        prob = {'f': J, 'x': vertcat(*w),'g': vertcat(*g)}
        opts={
            "ipopt.acceptable_tol":1e-8,
            "ipopt.acceptable_obj_change_tol":1e-6,
            "ipopt.print_level":1
        }


        solver = nlpsol('solver', 'ipopt', prob,opts)
        sol = solver(x0=w0, lbx=lbw, ubx=ubw, lbg=lbg, ubg=ubg)
        sol_speed = sol['x'][0]
        print("Machine was set to(setspeed, angle, spin, tf):", [setspeed, angle, spin, tf])
        print("Real speed based on actual landingpoint is:", float(sol_speed))
        return float(sol_speed)  

    def ballpathfunction(self,t,y):
        #y_0=[x_0,y_0,z_0,dx_0,dy_0,dz_0;v_0;omega_0;lambda;gamma;k_d;k_l;k_w];
        g=9.81
        ydot=np.zeros(8)
        ydot[0]=y[3] 
        ydot[1]=y[4]
        ydot[2]=y[5] 
        ydot[3]=(self.k_l*y[7]*(np.sin(self.lambd)*np.sin(self.gamma)*y[5]-np.cos(self.lambd)*y[4])-self.k_d*y[6]*y[3]) 
        ydot[4]=(self.k_l*y[7]*(np.sin(self.lambd)*np.cos(self.gamma)*y[5]-np.cos(self.lambd)*y[3])-self.k_d*y[6]*y[4]) 
        ydot[5]=(self.k_l*y[7]*(np.sin(self.lambd)*np.cos(self.gamma)*y[4]-np.sin(self.lambd)*np.sin(self.gamma)*y[3])-self.k_d*y[6]*y[5]-g) 
        ydot[6]=(self.k_l*y[7]*((np.sin(self.lambd)*np.sin(self.gamma)*y[5]-np.cos(self.lambd)*y[4])+(np.sin(self.lambd)*np.cos(self.gamma)*y[5]-np.cos(self.lambd)*y[3])+(np.sin(self.lambd)*np.cos(self.gamma)*y[4]-np.sin(self.lambd)*np.sin(self.gamma)*y[3]))/(y[6]) -self.k_d*(y[3]+y[4]+y[5])) 
        ydot[7]=(-self.k_w*y[7]*y[7]) 

        # ydot=np.zeros(13)
        # ydot[0]=y[3]
        # ydot[1]=y[4]
        # ydot[2]=y[5]
        # ydot[3]=y[11]*y[7]*(np.sin(y[8])*np.sin(y[9])*y[5]-np.cos(y[8])*y[4])-y[10]*y[6]*y[3]
        # ydot[4]=y[11]*y[7]*(np.sin(y[8])*np.cos(y[9])*y[5]-np.cos(y[8])*y[3])-y[10]*y[6]*y[4]
        # ydot[5]=y[11]*y[7]*(np.sin(y[8])*np.cos(y[9])*y[4]-np.sin(y[8])*np.sin(y[9])*y[3])-y[10]*y[6]*y[5]-g
        # ydot[6]=y[11]*y[7]*((np.sin(y[8])*np.sin(y[9])*y[5]-np.cos(y[8])*y[4])+(np.sin(y[8])*np.cos(y[9])*y[5]-np.cos(y[8])*y[3])+(np.sin(y[8])*np.cos(y[9])*y[4]-np.sin(y[8])*np.sin(y[9])*y[3]))/y[6] -y[10]*(y[3]+y[4]+y[5])
        # ydot[7]=-y[12]*y[7]*y[7]
        # ydot[8]=0
        # ydot[9]=0
        # ydot[10]=0
        # ydot[11]=0
        # ydot[12]=0
        return ydot
    
    def aboveground(self,path):
        #filter path to only contain points z>0
        m=np.size(path,0)
        n=np.size(path,1)
        pathabove=np.zeros((m,n))
        end_point= 0
        for i in range(0,m):
            if path[i,2]>=0:
                pathabove[i]=path[i]
            else:
                end_point=i
                break
        pathabove=pathabove[0:end_point]
        return pathabove

    def above_z(self,path,z):
        #filter path to only contain points z>0
        peak=0
        m=np.size(path,0)
        n=np.size(path,1)
        pathabove=np.zeros((m,n))
        end_point= 0
        for i in range(0,m):
            if path[i,2]>=z:
                pathabove[i]=path[i]
                peak=1
            elif not peak:
                pathabove[i]=path[i]
            else:
                end_point=i
                break
        pathabove=pathabove[0:end_point]
        return pathabove

    def Simulate_ballpath(self,y_0):
        t0, t1 = 0, 10  
        t = np.linspace(t0, t1, 10000) 


        y_sol = np.zeros((len(t), len(y_0))) 
        y_sol[0, :] = y_0

        r = integrate.ode(self.ballpathfunction).set_integrator("dopri5") 
        r.set_initial_value(y_0, t0) 
        for i in range(1, t.size):
            y_sol[i, :] = r.integrate(t[i]) 
            if not r.successful():
                raise RuntimeError("Could not integrate")

        return [t,y_sol]

    def find_y0(self,x):
        dx_0=x[0]*np.cos(x[1])*np.sin(self.theta)
        dy_0=x[0]*np.cos(x[1])*np.cos(self.theta)
        dz_0=x[0]*np.sin(x[1])
        y_0 = [0,0.1,0.1,dx_0,dy_0,dz_0,x[0],x[2]]
        #y_0 = [0,0.1,0.1,dx_0,dy_0,dz_0,x[0],x[2]]
        #y_0=[startpoint[0],startpoint[1],startpoint[2],dx_0,dy_0,dz_0,v_0,omega_0,lambda_0,gamma,k_d,k_l,k_w]
        return y_0

    def plot_path(self,speed,angle,spin):
        x=[speed,angle,spin]
        y_0 = self.find_y0(x)
        print(y_0)
        _,y_s=self.Simulate_ballpath(y_0)
        path = self.aboveground(y_s[:,0:3])
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        if abs(spin)<=0.01: 
            ax.set_xlim([-1,1])
        ax.plot(path[:,0], path[:,1], path[:,2], label='parametric curve')
        ax.legend()
        plt.show()

# optim=Optimizer()
# x=[-2,15,0]
# # sol_speed,sol_angle,sol_spin,sol_tf=optim.find_initvalues_spin(x)
# # print("ALTSÅ VERDIENE ER: ",sol_speed,sol_angle*180/np.pi,sol_spin)
# optim.plot_path(10,45*np.pi/180,0.018)
# landingpoint=[0.8,14,0]
# speed = optim.calculate_real_speed(landingpoint, sol_speed, sol_angle, sol_spin, sol_tf)
# optim.plot_path(speed,sol_angle,sol_spin)