classdef logique

    methods(Static)

        % Following properties of 'maskInitContext' are available to use:
        %  - BlockHandle 
        %  - MaskObject 
        %  - MaskWorkspace: Use get/set APIs to work with mask workspace.
    function MaskInitialization(maskInitContext)
        blk = getfullname(maskInitContext.BlockHandle);
        if strcmp(get_param(blk, 'Enregistrement'), 'on')
            set_param([blk '/Enregistrement'], 'Value', '1');
        else
            set_param([blk '/Enregistrement'], 'Value', '0');
        end
    end
        % Use the code browser on the left to add the callbacks.


        
    end
end