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

            if ws.get('K') ~= 0
                %si on spécifie le pid
                K = ws.get('K');
                Ti = ws.get('Ti');
                Td = ws.get('Td');

                if Consigne > T_init
                    %chauffage
    
                   if ws.get('K1') ~= 0
                       K1 = ws.get('K1');
                       T1 = ws.get('T1');
                   else
                       if T_init < 23
                           K1 = 0.007628;
                           T1 = 0.01103;
                       else
                           K1 = 0.00881;
                           T1 = 0.01194;
                        end
                   end
                   if ws.get('K2') ~= 0
                       K2 = ws.get('K2');
                       T2 = ws.get('T2');
                   else
                       if T_init < 23
                           K2 = 0.03405;
                           T2 = 0.03035;
                       else
                           K2 = 0.02418;
                           T2 = 0.02359;
                        end
                   end
                   if ws.get('K3') ~= 0
                       K3 = ws.get('K3');
                       T3 = ws.get('T3');
                   else
                       if T_init < 23
                           K3 = 0.04391;
                           T3 = 0.04924;
                       else
                           K3 = 0.04385;
                           T3 = 0.04942;
                        end
                   end
                else
                    %refroidissement
                    if ws.get('K1') ~= 0
                        K1 = ws.get('K1');
                        T1 = ws.get('T1');
                   else
                       if T_init < 25
                           K1 = 0.00751;
                           T1 = 0.01415;
                       else
                           K1 = 0.01043;
                           T1 = 0.01371;
                        end
                    end
                    if ws.get('K2') ~= 0
                        K2 = ws.get('K2');
                        T2 = ws.get('T2');
                   else
                       if T_init < 25
                           K2 = 0.02219;
                           T2 = 0.02201;
                       else
                           K2 = 0.02568;
                           T2 = 0.0256;
                        end
                    end
                    if ws.get('K3') ~= 0
                        K3 = ws.get('K3');
                        T3 = ws.get('T3');
                   else
                       if T_init < 25
                           K3 = 0.3512;
                           T3 = 0.3473;
                       else
                           K3 = 0.03719;
                           T3 = 0.04271;
                        end
                    end
                    if ws.get('az') ~= 0
                    az = ws.get('az');
                    else
                        if T_init < 23
                            az = 0.01084;
                        else
                            az = 0.1083;
                        end
                    end
                    if ws.get('bz') ~= 0
                        bz = ws.get('bz');
                    else
                        if T_init < 23
                            bz = -0.9757;
                        else
                            bz = -0.9756;
                        end
                    end
                end
            else
                %si on spécifie pas le pid
                if Consigne > T_init
                    %chauffage
                    K = 9.2;
                    Ti = 250;
                    Td = 35;
    
                   if ws.get('K1') ~= 0
                       K1 = ws.get('K1');
                       T1 = ws.get('T1');
                   else
                       if T_init < 23
                           K1 = 0.007628;
                           T1 = 0.01103;
                       else
                           K1 = 0.00881;
                           T1 = 0.01194;
                        end
                   end
                   if ws.get('K2') ~= 0
                       K2 = ws.get('K2');
                       T2 = ws.get('T2');
                   else
                       if T_init < 23
                           K2 = 0.03405;
                           T2 = 0.03035;
                       else
                           K2 = 0.02418;
                           T2 = 0.02359;
                        end
                   end
                   if ws.get('K3') ~= 0
                       K3 = ws.get('K3');
                       T3 = ws.get('T3');
                   else
                       if T_init < 23
                           K3 = 0.04391;
                           T3 = 0.04924;
                       else
                           K3 = 0.04385;
                           T3 = 0.04942;
                        end
                   end
                else
                    %refroidissement
                    K = 10.5;
                    Ti = 230;
                    Td = 40;
                    if ws.get('K1') ~= 0
                        K1 = ws.get('K1');
                        T1 = ws.get('T1');
                   else
                       if T_init < 25
                           K1 = 0.00751;
                           T1 = 0.01415;
                       else
                           K1 = 0.01043;
                           T1 = 0.01371;
                        end
                    end
                    if ws.get('K2') ~= 0
                        K2 = ws.get('K2');
                        T2 = ws.get('T2');
                   else
                       if T_init < 25
                           K2 = 0.02219;
                           T2 = 0.02201;
                       else
                           K2 = 0.02568;
                           T2 = 0.0256;
                        end
                    end
                    if ws.get('K3') ~= 0
                        K3 = ws.get('K3');
                        T3 = ws.get('T3');
                   else
                       if T_init < 25
                           K3 = 0.3512;
                           T3 = 0.3473;
                       else
                           K3 = 0.03719;
                           T3 = 0.04271;
                        end
                    end
                    if ws.get('az') ~= 0
                    az = ws.get('az');
                    else
                        if T_init < 23
                            az = 0.01084;
                        else
                            az = 0.1083;
                        end
                    end
                    if ws.get('bz') ~= 0
                        bz = ws.get('bz');
                    else
                        if T_init < 23
                            bz = -0.9757;
                        else
                            bz = -0.9756;
                        end
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