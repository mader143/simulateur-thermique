classdef logique
    methods(Static)
        function MaskInitialization(maskInitContext)
            blk = getfullname(maskInitContext.BlockHandle);
            ws = maskInitContext.MaskWorkspace;
            enreg = ws.get('Enregistrement');
            temps = ws.get('Temps');
            
            set_param('simulink_1avrilhaha', 'StopTime', num2str(temps));
            
            if strcmp(enreg, 'on')
                ws.set('val_enreg', 1);
            else
                ws.set('val_enreg', 0);
            end
        end

        function Control3(~)
            sim('simulink_1avrilhaha')
        end
    end
end