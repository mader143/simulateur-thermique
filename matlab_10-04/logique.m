classdef logique
    methods(Static)
        function MaskInitialization(maskInitContext)
            % 1. Récupération des objets de base
            blk = getfullname(maskInitContext.BlockHandle);
            ws = maskInitContext.MaskWorkspace;
            
            % 2. Récupération des paramètres d'entrée
            enreg = ws.get('Enregistrement');
            temps = ws.get('Temps');
            PWM = ws.get('PWM');
            T_init = ws.get('T_init');
            
            % Mise à jour du temps de simulation du modèle
            set_param('simulink_08_04_procede', 'StopTime', num2str(temps));

            % 3. Logique de détermination des paramètres K et T
            % On utilise des variables locales pour le calcul
            if PWM > 0
                % --- MODE CHAUFFAGE ---
                seuil = 23;
                
                % Paramètre K1 / T1
                if ws.get('K1') ~= 0
                    currentK1 = ws.get('K1'); currentT1 = ws.get('T1');
                else
                    if T_init < seuil
                        currentK1 = 0.007628; currentT1 = 0.01103;
                    else
                        currentK1 = 0.00881;  currentT1 = 0.01194;
                    end
                end
                
                % Paramètre K2 / T2
                if ws.get('K2') ~= 0
                    currentK2 = ws.get('K2'); currentT2 = ws.get('T2');
                else
                    if T_init < seuil
                        currentK2 = 0.03405;  currentT2 = 0.03035;
                    else
                        currentK2 = 0.02418;  currentT2 = 0.02359;
                    end
                end
                
                % Paramètre K3 / T3
                if ws.get('K3') ~= 0
                    currentK3 = ws.get('K3'); currentT3 = ws.get('T3');
                else
                    if T_init < seuil
                        currentK3 = 0.04391;  currentT3 = 0.04924;
                    else
                        currentK3 = 0.04385;  currentT3 = 0.04942;
                    end
                end
                
            else
                % --- MODE REFROIDISSEMENT ---
                seuil = 25;
                
                % Paramètre K1 / T1
                if ws.get('K1') ~= 0
                    currentK1 = ws.get('K1'); currentT1 = ws.get('T1');
                else
                    if T_init < seuil
                        currentK1 = 0.00751;  currentT1 = 0.01415;
                    else
                        currentK1 = 0.01043;  currentT1 = 0.01371;
                    end
                end
                
                % Paramètre K2 / T2
                if ws.get('K2') ~= 0
                    currentK2 = ws.get('K2'); currentT2 = ws.get('T2');
                else
                    if T_init < seuil
                        currentK2 = 0.02219;  currentT2 = 0.02201;
                    else
                        currentK2 = 0.02568;  currentT2 = 0.0256;
                    end
                end
                
                % Paramètre K3 / T3
                if ws.get('K3') ~= 0
                    currentK3 = ws.get('K3'); currentT3 = ws.get('T3');
                else
                    if T_init < seuil
                        currentK3 = 0.3512;   currentT3 = 0.3473;
                    else
                        currentK3 = 0.03719;  currentT3 = 0.04271;
                    end
                end
            end

            % 4. Injection des valeurs calculées dans le Workspace du bloc
            ws.set('K1', currentK1); ws.set('T1', currentT1);
            ws.set('K2', currentK2); ws.set('T2', currentT2);
            ws.set('K3', currentK3); ws.set('T3', currentT3);

            % 5. Gestion de l'enregistrement
            if strcmp(enreg, 'on')
                ws.set('val_enreg', 1);
            else
                ws.set('val_enreg', 0);
            end
        end

        function Control3(~)
            % 1. Lancer la simulation
            try
                out = sim('simulink_08_04_procede.slx');
                disp('Simulation terminée, début de l''exportation...');
                
                % 2. Récupérer les paramètres du masque
                blk = 'simulink_08_04_procede/Simulateur Équipe 5';
                enreg = get_param(blk, 'Enregistrement');
                nomBase = get_param(blk, 'Fichier');

                if strcmp(enreg, 'on')
                    % --- DOSSIER ET FICHIER ---
                    dossier = fileparts(which('simulink_08_04_procede.slx'));
                    
                    % Récupération des données simulées
                    t = out.tout;
                    y = out.Fichier; % Assurez-vous que le signal s'appelle bien "Fichier" dans Simulink

                    n = min(length(t), length(y));
                    % Matrice : [Temps, Sig1, Sig2, Sig3, Sig4]
                    dataMatrix = [t(1:n), y(1:n, 1:4)];

                    % Génération du nom de fichier unique
                    dateStr = datestr(now, '_yyyy-mm-dd_HH-MM'); % Format compatible anciennes versions
                    nomFichier = fullfile(dossier, [nomBase, dateStr, '.txt']);

                    % Sauvegarde format texte tabulé
                    writematrix(dataMatrix, nomFichier, 'Delimiter', 'tab');
                    fprintf('Fichier sauvegardé avec succès : %s\n', nomFichier);
                end
            catch e
                fprintf('Erreur lors de la simulation ou de l''exportation : %s\n', e.message);
            end
        end
    end
end