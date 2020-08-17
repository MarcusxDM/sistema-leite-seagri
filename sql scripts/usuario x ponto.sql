SELECT u.id, u.nome, u.email, u.cod_ibge_id,
		ponto.id, ponto.nome
	FROM public.relatorios_usuario as u, public.relatorios_ponto as ponto, 
	public.relatorios_ponto_membro as pm
	where u.id = pm.usuario_id and ponto.id = pm.ponto_id;
	
	
