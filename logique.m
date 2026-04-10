classdef logique
    methods(Static)
        function MaskInitialization(maskInitContext)
            blk = getfullname(maskInitContext.BlockHandle);
            ws = maskInitContext.MaskWorkspace;
            enreg = ws.get('Enregistrement');
            temps = ws.get('Temps');
            
            set_param('simulink_08_04_procede', 'StopTime', num2str(temps))
            disp('testtttttttt')
            Consigne = ws.get('Consigne');
            T_init = ws.get('T_init');
            K1 = ws.get('K1');
            T1 = ws.get('T1');
            K2 = ws.get('K2');
            T2 = ws.get('T2');
            K3 = ws.get('K3');
            T3 = ws.get('T3');
            disp(T_init)
            disp(Consigne)
            disp(T_init);

            if ws.get('K') ~= 0
                K = ws.get('K');
                Ti = ws.get('Ti');
                Td = ws.get('Td');
                if T_init < 23
                    K1 = 0.007628;
                    T1 = 0.01103;
                    K2 = 0.03405;
                    T2 = 0.03035;
                    K3 = 0.04391;
                    T3 = 0.04924;
                    az = 0.01084;
                    bz = -0.9757;
                else
                    K1 = 0.00881;
                    T1 = 0.01194;
                    K2 = 0.02418;
                    T2 = 0.02359;
                    K3 = 0.04385;
                    T3 = 0.04942;
                    az = 0.1083;
                    bz = -0.9756;
                end
            else

                if Consigne > T_init
                    K = 9.2;
                    Ti = 250;
                    Td = 35;
    
                    if T_init < 23
                        K1 = 0.007628;
                        T1 = 0.01103;
                        K2 = 0.03405;
                        T2 = 0.03035;
                        K3 = 0.04391;
                        T3 = 0.04924;
                        az = 0.01084;
                        bz = -0.9757;
                    else
                        K1 = 0.00881;
                        T1 = 0.01194;
                        K2 = 0.02418;
                        T2 = 0.02359;
                        K3 = 0.04385;
                        T3 = 0.04942;
                        az = 0.1083;
                        bz = -0.9756;
                    end
                else
                    K = 10.5;
                    Ti = 230;
                    Td = 40;
                    if T_init < 30
                        K1 = 0.00751;
                        T1 = 0.01415;
                        K2 = 0.02291;
                        T2 = 0.02201;
                        K3 = 0.3512;
                        T3 = 0.3473;
                        az = 0.08079;
                        bz = -0.8402;
                    else
                        K1 = 0.01043;
                        T1 = 0.01371;
                        K2 = 0.02568;
                        T2 = 0.0256;
                        K3 = 0.03719;
                        T3 = 0.04271;
                        az = 0.009199;
                        bz = -0.9789;
                    end
                end
            end
            ws.set('K1', K1);
            ws.set('T1', T1);
            ws.set('K2', K2);
            ws.set('T2', T2);
            ws.set('K3', K3);
            ws.set('T3', T3);
            ws.set('az', az);
            ws.set('bz', bz);
            ws.set('K', K);
            ws.set('Ti', Ti);
            ws.set('Td', Td);

              
           
            
            if strcmp(enreg, 'on')
                ws.set('val_enreg', 1);
            else
                ws.set('val_enreg', 0);
            end
        end

        function Control3(~)    
            sim('simulink_08_04_procede.slx');
            disp('testttt');
        end

  
    end
end